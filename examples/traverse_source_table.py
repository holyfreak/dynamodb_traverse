import asyncio
import time

from dynamodb_migration.counter import AsyncCounter
from dynamodb_migration.main import DynamoDBClient, cardinality
import dynamodb_migration.ddb_const as cst

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    guru = DynamoDBClient(queue=asyncio.Queue(loop=loop), **{'aws_access_key_id': 'myFakeKey', 'aws_secret_access_key': 'myFakeSecret'})

    config_table_name = 'dev_test_table_demo_1_2_150_20_3_3_3'

    if True:
        counter = AsyncCounter()
        start = time.perf_counter()


        async def main():
            async with guru.get_dynamodb() as dynamodb:
                table = dynamodb.Table(config_table_name)
                await guru.traverse_sync(
                    **{
                        cst.PRODUCER: {
                            cst.SOURCE_TABLE: table,
                            cst.THREAD_COUNT: 3,
                            cst.SCAN_BATCH_SIZE: 35,
                            # INDEXNAME: 'indexname'
                        },
                        cst.CONSUMER: {
                            cst.THREAD_COUNT: 3,
                            cst.FUNCTION: cardinality,
                            cst.TIMEOUT: 3,
                            cst.ARGS: [AsyncCounter()]
                        }
                    }
                )


        loop.run_until_complete(main())
        elapsed = time.perf_counter() - start
        loop.close()
        print(f'finished in {elapsed:0.5f} sec')
