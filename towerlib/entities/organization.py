#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: organization.py
#
# Copyright 2018 Costas Tyfoxylos
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
Main code for organization

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import json
import logging

from towerlib.towerlibexceptions import (InvalidUserLevel,
                                         InvalidUser,
                                         InvalidTeam,
                                         InvalidVariables,
                                         InvalidInventory,
                                         InvalidCredential,
                                         InvalidProject)
from .user import User
from .inventory import Inventory
from .core import Entity, USER_LEVELS
from .team import Team
from .project import Project
from .credential import Credential

__author__ = '''Costas Tyfoxylos <ctyfoxylos@schubergphilis.com>'''
__docformat__ = '''google'''
__date__ = '''2018-01-03'''
__copyright__ = '''Copyright 2018, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos"]
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<ctyfoxylos@schubergphilis.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# This is the main prefix used for logging
LOGGER_BASENAME = '''organization'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class Organization(Entity):  # pylint: disable=too-many-public-methods
    """Models the organization entity of ansible tower"""

    def __init__(self, tower_instance, data):
        Entity.__init__(self, tower_instance, data)

    @property
    def name(self):
        """The name of the Organization

        Returns:
            string: The name of the organization

        """
        return self._data.get('name')

    @property
    def description(self):
        """The description of the Organization

        Returns:
            string: The descrption of the Organization

        """
        return self._data.get('description')

    @property
    def created_by(self):
        """The User that created the organization

        Returns:
            User: The user that created the organization in tower

        """
        url = self._data.get('related', {}).get('created_by')
        return self._tower._get_object_by_url('User', url)  # pylint: disable=protected-access

    @property
    def modified_by(self):
        """The User that modified the organization last

        Returns:
            User: The user that modified the organization in tower last

        """
        url = self._data.get('related', {}).get('modified_by')
        return self._tower._get_object_by_url('User', url)  # pylint: disable=protected-access

    @property
    def object_roles(self):
        """The object roles

        Returns:
            ObjectRole: The object roles supported

        """
        url = self._data.get('related', {}).get('object_roles')
        return self._tower._get_object_list_by_url('ObjectRole', url)  # pylint: disable=protected-access

    @property
    def object_role_names(self):
        """The names of the object roles

        Returns:
            list: A list of strings for the object_roles

        """
        return [object_role.name for object_role in self.object_roles]

    @property
    def job_templates_count(self):
        """The number of job templates of the organization

        Returns:
            integer: The count of the job templates on the organization

        """
        return self._data.get('related_field_counts', {}).get('job_templates', 0)

    @property
    def users_count(self):
        """The number of user of the organization

        Returns:
            integer: The count of the users on the organization

        """
        return self._data.get('related_field_counts', {}).get('users', 0)

    @property
    def teams_count(self):
        """The number of teams of the organization

        Returns:
            integer: The count of the teams on the organization

        """
        return self._data.get('related_field_counts', {}).get('teams', 0)

    @property
    def admins_count(self):
        """The number of administrators of the organization

        Returns:
            integer: The count of the administrators on the organization

        """
        return self._data.get('related_field_counts', {}).get('admins', 0)

    @property
    def inventories_count(self):
        """The number of inventories of the organization

        Returns:
            integer: The count of the inventories on the organization

        """
        return self._data.get('related_field_counts', {}).get('inventories', 0)

    @property
    def projects_count(self):
        """The number of projects of the organization

        Returns:
            integer: The count of the projects on the organization

        """
        return self._data.get('related_field_counts', {}).get('projects', 0)

    @property
    def projects(self):
        """The projects of the organization

        Returns:
            list: A list of Projects for the organization

        """
        url = self._data.get('related', {}).get('projects')
        return self._tower._get_object_list_by_url('Project', url)  # pylint: disable=protected-access

    def create_project(self,  # pylint: disable=too-many-arguments
                       name,
                       description,
                       credential,
                       scm_url,
                       scm_branch='master',
                       scm_type='git',
                       scm_clean=True,
                       scm_delete_on_update=False,
                       scm_update_on_launch=True,
                       scm_update_cache_timeout=0):
        """Creates a project in the organization

        Args:
            name: The name of the project
            description: The description of the project
            credential: The name of the credential to use for the project
            scm_url: The url of the scm
            scm_branch: The default branch of the scm
            scm_type: The type of the scm
            scm_clean: Clean scm or not Boolean
            scm_delete_on_update: Delete scm on update Boolean
            scm_update_on_launch: Update scm on launch Boolean
            scm_update_cache_timeout: Scm cache update integer

        Returns:
            Project: The created project on success, None otherwise

        Raises:
            InvalidOrganization: The organization provided as argument does not exist.

        Raises:
            InvalidCredential: The credential provided as argument does not exist.

        """
        url = '{api}/projects/'.format(api=self._tower.api)
        credential_ = self._tower.get_credential_by_name(credential)
        if not credential_:
            raise InvalidCredential(credential)
        payload = {'name': name,
                   'description': description,
                   'scm_type': scm_type,
                   'base_dir': self._tower.configuration.project_base_dir,
                   'scm_url': scm_url,
                   'scm_branch': scm_branch,
                   'scm_clean': scm_clean,
                   'scm_delete_on_update': scm_delete_on_update,
                   'credential': credential_.id,
                   'timeout': 0,
                   'organization': self.id,
                   'scm_update_on_launch': scm_update_on_launch,
                   'scm_update_cache_timeout': scm_update_cache_timeout}
        response = self._tower.session.post(url, data=json.dumps(payload))
        return Project(self._tower, response.json()) if response.ok else None

    def delete_project(self, name):
        """Deletes a project by username

        Args:
            name: The name of the project to delete

        Returns:
            bool: True on success, False otherwise

        Raises:
            InvalidProject: The project provided as argument does not exist.

        """
        project = next((project for project in self._tower.project
                        if project.name.lower() == name.lower()), None)
        if not project:
            raise InvalidProject(name)
        return project.delete()

    @property
    def users(self):
        """The users of the organization

        Returns:
            list of User: A list of User objects for the users of the organization

        """
        url = '{organization}users/'.format(organization=self.url)
        results = self._tower._get_paginated_response(url)  # pylint: disable=protected-access
        return [User(self._tower, data) for data in results]

    def create_user(self,  # pylint: disable=too-many-arguments
                    first_name,
                    last_name,
                    email,
                    username,
                    password,
                    level='standard'):
        """Creates a user under the organization

        Args:
            first_name: The first name of the user
            last_name: The last name of the user
            email: The email of the user
            username: The username to create for the user
            password: The password to set for the user
            level: The type of the account (standard|system_auditor|system_administrator)

        Returns:
            User: The created User object on success, None otherwise

        Raises:
            InvalidHost: The host provided as argument does not exist.

        """
        if level not in USER_LEVELS:
            raise InvalidUserLevel(level)
        url = '{organization}users/'.format(organization=self.url)
        payload = {'first_name': first_name,
                   'last_name': last_name,
                   'organization': self.id,
                   'email': email,
                   'username': username,
                   'password': password,
                   'password_confirm': password,
                   'user_type': {'type': 'normal',
                                 'label': 'Normal User'},
                   'is_superuser': False,
                   'is_system_auditor': False}
        if level == 'system_auditor':
            payload['user_type'] = {'type': 'system_auditor',
                                    'label': 'System Auditor'}
            payload['is_system_auditor'] = True
        elif level == 'system_administrator':
            payload['user_type'] = {'type': 'system_administrator',
                                    'label': 'System Administrator'}
            payload['is_superuser'] = True
        response = self._tower.session.post(url, data=json.dumps(payload))
        return User(self._tower, response.json()) if response.ok else None

    def delete_user(self, username):
        """Deletes a user by username

        Args:
            username: The username of the user to delete

        Returns:
            bool: True on success, False otherwise

        Raises:
            InvalidUser: The username provided as argument does not exist.

        """
        user = next((user for user in self._tower.users
                     if user.username.lower() == username.lower()), None)
        if not user:
            raise InvalidUser(username)
        return user.delete()

    @property
    def teams(self):
        """The teams of the organization

        Returns:
            list of Team: A list of Team objects for the teams of the organization

        """
        url = '{organization}teams/'.format(organization=self.url)
        results = self._tower._get_paginated_response(url)  # pylint: disable=protected-access
        return [Team(self._tower, data) for data in results]

    def create_team(self, name, description):
        """Creates a team

        Args:
            name: The name of the team to create
            description: The description of the team

        Returns:
            Team: The created Team object on success, None otherwise

        """
        payload = {'name': name,
                   'description': description,
                   'organization': self.id}
        url = '{api}/teams/'.format(api=self._tower.api)
        response = self._tower.session.post(url, data=json.dumps(payload))
        return Team(self._tower, response.json()) if response.ok else None

    def delete_team(self, name):
        """Deletes a team by name

        Args:
            name: The name of the team to delete

        Returns:
            bool: True on success, False otherwise

        Raises:
            InvalidTeam: The team provided as argument does not exist.

        """
        team = next((team for team in self._tower.teams
                     if team.name.lower() == name.lower()), None)
        if not team:
            raise InvalidTeam(name)
        return team.delete()

    @property
    def inventories(self):
        """The inventories of the organization

        Returns:
            list of Inventory: A list of Inventory objects for the inventories of the organization

        """
        url = '{organization}inventories/'.format(organization=self.url)
        results = self._tower._get_paginated_response(url)  # pylint: disable=protected-access
        return [Inventory(self._tower, data) for data in results]

    def create_inventory(self, name, description, variables='{}'):
        """Creates an inventory

        Args:
            name: The name of the inventory to create
            description: The description of the inventory
            variables: A json with the initial variables set on the inventory

        Returns:
            Inventory: The created Inventory object on success, None otherwise

        Raises:
            InvalidVariables: The variables provided as argument is not valid json.

        """
        try:
            variables = json.loads(variables)
        except ValueError:
            raise InvalidVariables(variables)
        payload = {'name': name,
                   'description': description,
                   'organization': self.id,
                   'variables': variables}
        url = '{api}/inventories/'.format(api=self._tower.api)
        response = self._tower.session.post(url, data=json.dumps(payload))
        return Inventory(self._tower, response.json()) if response.ok else None

    def delete_inventory(self, name):
        """Deletes an inventory by name

        Args:
            name: The name of the inventory to delete

        Returns:
            bool: True on success, False otherwise

        Raises:
            InvalidHInventory: The inventory provided as argument does not exist.

        """
        inventory = next((inventory for inventory in self._tower.inventories
                          if inventory.name.lower() == name.lower()), None)
        if not inventory:
            raise InvalidInventory(name)
        return inventory.delete()

    @property
    def credentials(self):
        """The credentials of the organization

        Returns:
            list: A list of Credential objects for the credentials of the organization

        """
        url = '{organization}credentials/'.format(organization=self.url)
        results = self._tower._get_paginated_response(url)  # pylint: disable=protected-access
        return [Credential(self._tower, data) for data in results]

    def get_credential_by_name(self, name):
        """Retrieves a credential by name

        Args:
            name: The name of the credential to retrieve

        Returns:
            Host: The credential if a match is found else None

        """
        return next((credential for credential in self.credentials
                     if credential.name.lower() == name.lower()), None)

    def get_credential_by_id(self, id_):
        """Retrieves a credential by id

        Args:
            id_: The id of the credential to retrieve

        Returns:
            Host: The credential if a match is found else None

        """
        return next((credential for credential in self.credentials
                     if credential.id == id_), None)

    # def create_credential_in_organization(self,
    #                                       organization,
    #                                       name,
    #                                       description,
    #                                       user,
    #                                       team,
    #                                       credential_type,
    #                                       inputs_='{}'):
    #     """Creates a credential under an organization
    #
    #     Args:
    #         organization: The name of the organization to create a credential under
    #         name: The name of the credential to create
    #         description: The description of the credential to create
    #         user: The username of the user to assign to the credential
    #         team: The name of the team to assign to the credential
    #         credential_type: The name of the type of the credential
    #         inputs_: A json with the values to set to the credential according to what is required by its type
    #
    #     Returns:
    #         Credential: The created credential upon success, None otherwise
    #
    #     Raises:
    #         InvalidOrganization: The organization provided as argument does not exist.
    #         InvalidUser: The user provided as argument does not exist.
    #         InvalidTeam: The team provided as argument does not exist.
    #         InvalidCredentialType: The credential type provided as argument does not exist.
    #         InvalidVariables: The inputs provided as argument is not valid json.
    #
    #     """
    #     organization_ = self.get_organization_by_name(organization)
    #     if not organization_:
    #         raise InvalidOrganization(organization)
    #     user_ = self.get_user_by_username(user)
    #     if not user_:
    #         raise InvalidUser(user)
    #     team_ = self.get_team_by_name(team)
    #     if not team_:
    #         raise InvalidTeam(team)
    #     credential_type_ = self.get_credential_type_by_name(credential_type)
    #     if not credential_type_:
    #         raise InvalidCredentialType(credential_type)
    #     payload = {'name': name,
    #                'description': description,
    #                'organization': organization_.id,
    #                'user': user_.id,
    #                'team': team_.id,
    #                'credential_type': credential_type_.id}
    #     try:
    #         payload['inputs'] = json.loads(inputs_)
    #     except ValueError:
    #         raise InvalidVariables(inputs_)
    #     url = '{api}/credentials/'.format(api=self.api)
    #     response = self.session.post(url, data=json.dumps(payload))
    #     return Credential(self, response.json()) if response.ok else None
