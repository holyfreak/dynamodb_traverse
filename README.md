# dynamodb_migration
High performance, thread safe migration tool for AWS DynamoDB based on aioboto3.

### Installation/Uninstallation
Prerequisite: aioboto3>=6.4.1

Run following command to install requirements:

`pip install aioboto3`

Next, install dynamodb-migration by running:

`pip install dynamodb-migration`

To uninstall dynamodb-migration, run:

`pip uninstall dynamodb-migration`

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
                
                # check document for the schema of the parameters 
                await client.traverse_sync(
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

### API document (in progress)

### Benchmark (in progress)

### Road map
We are currently working on a distributed migration tool that takes migration tasks execution to next level. So stay tuned!  


