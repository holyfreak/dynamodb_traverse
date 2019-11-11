import collections
import configparser
import json
from datetime import datetime
from os.path import expanduser

import boto3

from dynamodb_traverse.perf import time_in_millis
from dynamodb_traverse.base import Base


class AWSBase(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.my_aws_config = configparser.ConfigParser()
        self.my_aws_path = kwargs.pop("my_aws_path", "/".join([expanduser('~'), '.aws/credentials']))
        self.my_aws_config.read(self.my_aws_path)

        profile = kwargs.pop("profile", "default")
        self.my_aws_access_key_id = self.my_aws_config[profile]['aws_access_key_id']
        self.my_aws_secret_access_key = self.my_aws_config[profile]['aws_secret_access_key']

    def get_resource(self, resource_name, **kwargs):
        region = kwargs.pop("region", 'us-east-1')
        mysession = boto3.session.Session(
            aws_access_key_id=self.my_aws_access_key_id,
            aws_secret_access_key=self.my_aws_secret_access_key,
            region_name=region)
        return mysession.resource(resource_name, **kwargs)

    def connect(self, **kwargs):
        region = kwargs.pop("region", 'us-east-1')
        mysession = boto3.session.Session(
            aws_access_key_id=self.my_aws_access_key_id,
            aws_secret_access_key=self.my_aws_secret_access_key,
            region_name=region)
        return mysession.client(**kwargs)

    def connect_with_sts(self, **kwargs):
        aws_identity_path = kwargs.pop("aws_identity_path", "/".join((expanduser('~'), 'aws.identity.json')))

        def _mfa_number():
            try:
                with open(aws_identity_path, 'r') as f:
                    _d = json.load(f)
                return _d['Arn'].replace('user', 'mfa')
            except:
                raise Exception("aws identity not configured")

        aws_path = kwargs.pop("aws_token_path", "/".join((expanduser('~'), 'token.json')))

        with open(aws_path) as f:
            aws_config = json.load(f)

        if not aws_config or 'Credentials' not in aws_config or time_in_millis(
                datetime.strptime(aws_config['Credentials']['Expiration'], '%Y-%m-%d %H:%M:%S+00:00')) <= datetime.now().timestamp() * 1000:
            sts_client_session = boto3.session.Session(
                aws_access_key_id=self.my_aws_access_key_id,
                aws_secret_access_key=self.my_aws_secret_access_key)

            sts_client = sts_client_session.client('sts')

            # default accept code from stdin
            code = input("two factor auth code: ")

            resp = sts_client.get_session_token(
                DurationSeconds=129600,
                SerialNumber=_mfa_number(),
                TokenCode=code
            )
            aws_config = collections.defaultdict(dict)
            aws_config['Credentials']['SessionToken'] = resp['Credentials']['SessionToken']
            aws_config['Credentials']['AccessKeyId'] = resp['Credentials']['AccessKeyId']
            aws_config['Credentials']['SecretAccessKey'] = resp['Credentials']['SecretAccessKey']
            aws_config['Credentials']['Expiration'] = str(resp['Credentials']['Expiration'])

            with open(aws_path, 'w', encoding='utf-8') as f:
                json.dump(aws_config, f)

        region = kwargs.pop("region", 'us-east-1')
        mysession = boto3.session.Session(
            aws_session_token=aws_config['Credentials']['SessionToken'],
            aws_access_key_id=aws_config['Credentials']['AccessKeyId'],
            aws_secret_access_key=aws_config['Credentials']['SecretAccessKey'],
            region_name=region)

        return mysession.client(kwargs.pop('service', 's3'))
