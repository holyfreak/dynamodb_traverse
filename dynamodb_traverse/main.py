import asyncio
from pprint import pprint
import time
import aioboto3
from boto3.dynamodb.conditions import Key

from dynamodb_traverse import ddb_const as cst
from dynamodb_traverse.aws_base import AWSBase
from dynamodb_traverse.counter import AsyncCounter


async def table_query_pk(table, **query):
    if _table := table:
        if pk := query.pop('pk', None):
            if pkv := query.pop('pkv', None):
                return await _table.query(KeyConditionExpression=Key(pk).eq(pkv))
    raise ValueError


async def table_query(table, **query):
    if _table := table:
        return await _table.query(**query)
    raise ValueError


async def index_query_pk(table, **query):
    if _table := table:
        if index_name := query.pop('index_name', None):
            if gsik := query.pop('gsik', None):
                if gsikv := query.pop('gsikv', None):
                    return await _table.query(
                        IndexName=index_name,
                        KeyConditionExpression=Key(gsik).eq(gsikv)
                    )
    raise ValueError


async def index_query(table, **query):
    if _table := table:
        return await _table.query(**query)
    raise ValueError


async def cardinality(response, *consumer_args):
    for _ in response['Items']:
        pprint("current total = {}".format(str(consumer_args[0].increment())))


async def request(segment, exclusive_key, **config):
    if source := config.pop(cst.SOURCE_TABLE, None):
        if exclusive_key:
            return await source.scan(
                Segment=segment,
                ExclusiveStartKey=exclusive_key,
                **config)
        else:
            return await source.scan(
                Segment=segment,
                **config
            )


def init_table(client, **schema):
    try:
        tables = client.list_tables()
        if schema['TableName'] in tables['TableNames']:
            client.delete_table(TableName=schema['TableName'])
            time.sleep(2)
            while True:
                tables = client.list_tables()  # to change
                if schema['TableName'] in tables['TableNames']:
                    time.sleep(3)
                else:
                    break
        client.create_table(**schema)
        waiter = client.get_waiter('table_exists')
        waiter.wait(TableName=schema['TableName'])
        return 0
    except:
        return 1


class DynamoDBClient(AWSBase):
    def __init__(self, queue, local=True, **kwargs):
        super().__init__(**kwargs)
        self.local = local
        self.queue = queue

    def get_dynamodb(self):
        if self.local:
            return aioboto3.resource(cst.DYNAMODB, endpoint_url=cst.TEST_URL)
        else:
            return aioboto3.resource(cst.DYNAMODB)

    def get_client(self):
        if self.local:
            return aioboto3.client(cst.DYNAMODB, endpoint_url=cst.TEST_URL)
        else:
            return aioboto3.client(cst.DYNAMODB)

    async def traverse(self, **config):
        ps = [asyncio.create_task(self.produce(i, **config.get(cst.PRODUCER))) for i in range(config.get(cst.PRODUCER)[cst.THREAD_COUNT])] + [
            asyncio.create_task(self.consume(i, **config.get(cst.CONSUMER))) for i in range(config.get(cst.CONSUMER)[cst.THREAD_COUNT])]

        await asyncio.gather(*ps)

        self.logger.info("Traverse complete...")

    async def produce(self, segment, **config):
        _counter = iteration = 0
        cur = None
        while True:
            response = await request(segment, cur, **config)
            await self.queue.put(response)
            iteration += 1
            _counter += response['Count']

            self.logger.info(f"Producer #{segment} fetches {len(response['Items'])}"
                             f" at iteration {iteration}, total count = {_counter}"
                             f" q size ~ {self.queue.qsize()}")

            if cst.LAST_EVALUATED_KEY not in response:
                break
            else:
                cur = response[cst.LAST_EVALUATED_KEY]
        self.logger.info(f"Producer #{segment} fetched {_counter} items in total.")

    async def consume(self, segment, **config):
        while True:
            try:
                queued_item = await asyncio.wait_for(self.queue.get(), timeout=config[cst.TIMEOUT])
                if queued_item is None:
                    break
            except asyncio.TimeoutError:
                self.logger.error(f"consumer #{segment} timeout...")
                break
            try:
                await config[cst.FUNCTION](queued_item, *config[cst.ARGS])
            except Exception as e:
                self.logger.error(str(e))
                continue
            finally:
                self.queue.task_done()
