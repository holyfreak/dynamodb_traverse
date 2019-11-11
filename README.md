# dynamodb-traverse
High performance, thread safe, hackable traversing tool for AWS DynamoDB based on aioboto3.
<p align="center">
<a href="https://travis-ci/holyshipt/dynamodb_traverse"><img alt="Build Status" src="https://travis-ci.org/holyshipt/dynamodb_traverse.svg?branch=master"></a>
</p>

### Installation/Uninstallation
Prerequisite: python 3.8+ and aioboto3>=6.4.1 (bleeding edge)

Run following command to install requirements:

`pip install aioboto3`

Next, install dynamodb-traverse by running:

`pip install dynamodb-traverse`

To uninstall dynamodb-traverse, run:

`pip uninstall dynamodb-traverse`

### Usage

Here's a sample program to traverse through a demo table called "default":
```python

import asyncio
import time

from dynamodb_migration.counter import AsyncCounter
from dynamodb_migration.main import DynamoDBClient, cardinality
import dynamodb_migration.ddb_const as cst

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    
    # dynamodb-migration will look at your aws credentials defined at ~/.aws/credentials and pick up a profile named 'prod-api'
    # make sure it's correctly align to your environment
    client = DynamoDBClient(queue=asyncio.Queue(loop=loop), **{'profile': 'prod-api'})

    config_table_name = 'default'

    if True:
        # a counter to keep counting items being scanned
        counter = AsyncCounter()
        
        # here we define a coroutine as main entrance of our program
        async def main():
        
            # async context manager for dynamodb 
            async with client.get_dynamodb() as dynamodb:
                table = dynamodb.Table(config_table_name)
                
                # check API document section for complete schema of the parameters 
                await client.traverse(
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
        
        start = time.perf_counter()
        loop.run_until_complete(main())
        elapsed = time.perf_counter() - start
        loop.close()
        print(f'finished in {elapsed:0.5f} sec')
```

### create client
```
client = DynamoDBClient(
            queue=asyncio.Queue(loop=event_loop), 
            profile='string',
            log_file='string',
            local='boolean',
            **kwargs
         )
```

#### Parameters
* queue (Queue) [REQUIRED] - (async) in memory buffer queue 
    * event_loop (loop) [REQUIRED] - if use async queue, a loop need to be specified
* profile (string) [REQUIRED] - name of aws profile to use, which is defined in `.aws/credentials`
* local (boolean) [OPTIONAL] - a flag to indicate if it's local or prod env. Default to True.
* kwargs [OPTIONAL] - check [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#client) for advanced usage

### traverse
```
 client.traverse(**{
       'producer': {
           'source': 'string',
           'TotalSegments': 'number',
           'Limit': 'number',
           'IndexName': 'string',
            **kwargs
        },
       'consumer': {
           'TotalSegments': 'number',
           'function': 'function_label',
           'timeout': 'number',
           'args': 'list',
           **kwargs
        }
 })
```

#### Parameters
* producer (hash) [REQUIRED] - a hash describing the producer thread
    * source (string) [REQUIRED] - name of the source table in dynamodb
    * TotalSegments (number) [REQUIRED] - same in [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.scan)
    * Limit (number) [REQUIRED] - same in [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.scan)
    * IndexName (string) [OPTIONAL] - name of the source table index. If specified, we are scanning data from target index, instead of full table. 
    * kwargs (OPTIONAL) check [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.scan) for more advanced usage.
    
* consumer (hash) [REQUIRED] - a hash describing the consumer thread
    * TotalSegments (number) - same in [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.scan)
    * function (function_label) - pass a function to this consumer!
    * args (list) - pass a list of args to the function you just supplied. currently we only support position based args
    * timeout (number) - how many second should consumer wait if there's no work load available to it

### Benchmark (in progress)

### Road map
We are currently working on a distributed traversing tool that takes traversing tasks execution to next level. So stay tuned!  


