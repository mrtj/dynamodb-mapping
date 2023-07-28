=====
Usage
=====

DynamoDBMapping is an alternative API for `Amazon DynamoDB`_ that implements the Python
``collections.abc.MutableMapping`` abstract base class, effectively allowing you to use a DynamoDB
table as if it were a Python dictionary.

.. _Amazon DynamoDB: https://aws.amazon.com/dynamodb/


Getting started
---------------

To do anything useful with this module you need an Amazon Web Services account and an Amazon
DynamoDB table. In every AWS account several DynamoDB tables can be created for free. Open
an `AWS account`_ and `create a DynamoDB table`_. You also need to create a IAM user and configure
the access keys on your workstation. The easiest way to do so is to install and configure the
`AWS Command Line Interface`_. Once the AWS CLI works correctly, the AWS Python libraries (boto3)
will correctly pick up the credentials.

.. _AWS account: https://aws.amazon.com/free/
.. _create a DynamoDB table: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/getting-started-step-1.html
.. _AWS Command Line Interface: https://docs.aws.amazon.com/cli/index.html


Usage
-----

Once the credentials are correctly configured, you can start reading and writing to your DynamoDB
table with DynamoDBMapping as it was an ordinal Python dictionary::

    from dynamodb_mapping import DynamoDBMapping

    mapping = DynamoDBMapping(table_name="my_table")

    # Create or modify an item:
    mapping["my_item"] = {"description": "foo", "price": 123}
    mapping["my_item"]["price"] = 456

    # Iterate over all items:
    for key, value in mapping.items():
        print(key, value)

    # Get a single item:
    print(mapping["my_item"])

    # Number of items in table:
    # (read bellow on how to get the estimated vs precise number of items)
    print(len(mapping))

    # Delete an item:
    del mapping["my_item"]


All methods that iterate over the elements of the table do so in a lazy manner, in that the
successive pages of the scan operation are queried only on demand. Examples of such operations
include scan, iteration over keys, iteration over values, and iteration over items (key-value
tuples). You should pay particular attention to certain patterns that fetch all items in the table,
for example, calling ``list(mapping.values())``. This call will execute an exhaustive scan on your
table, which can be costly, and attempt to load all items into memory, which can be
resource-demanding if your table is particularly large.

The ``__len__`` implementation of this class returns a best-effort estimate of the number of items
in the table using the TableDescription DynamoDB API. The number of items are updated at DynamoDB
service side approximately once in every 6 hours. If you need the exact number of items currently in
the table, you can use ``len(list(mapping.keys()))``. Note however that this will cause to run an
exhaustive scan operation on your table.


Advanced configuration
----------------------

You have the following options to configure the underlying boto3 session:

- Automatic configuration: pass nothing to DynamoDBMapping initializer. This will prompt
  DynamoDBMapping to load the default ``boto3.Session`` object, which in turn will use the
  standard boto3 credentials chain to find AWS credentials (e.g., the ``~/.aws/credentials``
  file, environment variables, etc.).
- Pass a preconfigured ``boto3.Session`` object
- Pass ``aws_access_key_id`` and ``aws_secret_access_key`` as keyword arguments. Additionally,
  the optional ``aws_region`` and ``aws_profile`` arguments are also considered.

