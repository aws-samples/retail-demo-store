# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import requests
import boto3
from flask import current_app

class Users:

    def __init__(self):
        self.endpoint_lookup  = None

    def init_app(self, app):
        self.endpoint_lookup = EndpointLookupFactory(app)
        
    def get(self, user_id):
        users_service_host, users_service_port = self.endpoint_lookup.get_host_and_port()
        url = f'http://{users_service_host}:{users_service_port}/users/id/{user_id}'

        current_app.logger.info(f"Retrieving user info from {url}")
        response = requests.get(url)

        if response.ok:
            return response.json()
        current_app.logger.error(f"Error retrieving user info from {url}")
        return None

    class EndpointLookup:
        def __init__(self, app):
            self.service_host = app.config.get('USERS_SERVICE_HOST')
            self.service_port = app.config.get('USERS_SERVICE_PORT')

        def get_host_and_port(self):
            pass
         
    class AppConfig(EndpointLookup):
        def get_host_and_port(self):
            return self.service_host, self.service_port
    
    class ServiceDiscovery(EndpointLookup):
        def __init__(self, app):
            self.servicediscovery = boto3.client('servicediscovery')
            super().__init__(app)

        def get_host_and_port(self):
            response = self.servicediscovery.discover_instances(
                NamespaceName='retaildemostore.local',
                ServiceName='users',
                MaxResults=1,
                HealthStatus='HEALTHY'
            )
            service_host = response['Instances'][0]['Attributes']['AWS_INSTANCE_IPV4']
            return service_host, self.service_port

class EndpointLookupFactory:
    def __new__(cls, app) -> Users.EndpointLookup:
        service_host = app.config.get('USERS_SERVICE_HOST')
        discovery_type = 'ServiceDiscovery' if not service_host or service_host.strip().lower() == 'users.retaildemostore.local' else 'AppConfig'
        return getattr(Users, discovery_type)(app)