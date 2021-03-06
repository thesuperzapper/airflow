#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import uuid

from sqlalchemy import Boolean, Column, String, true as sqltrue
from sqlalchemy.orm import Session

from airflow.models.base import Base
from airflow.utils.session import provide_session


class KubeResourceVersion(Base):
    """Table containing Kubernetes Resource versions"""

    __tablename__ = "kube_resource_version"
    one_row_id = Column(Boolean, server_default=sqltrue(), primary_key=True)
    resource_version = Column(String(255))

    @staticmethod
    @provide_session
    def get_current_resource_version(session: Session = None) -> str:
        """Get Current Kubernetes Resource Version from Airflow Metadata DB"""
        (resource_version,) = session.query(KubeResourceVersion.resource_version).one()
        return resource_version

    @staticmethod
    @provide_session
    def checkpoint_resource_version(resource_version, session: Session = None) -> None:
        """Update Kubernetes Resource Version in Airflow Metadata DB"""
        if resource_version:
            session.query(KubeResourceVersion).update({
                KubeResourceVersion.resource_version: resource_version
            })
            session.commit()

    @staticmethod
    @provide_session
    def reset_resource_version(session: Session = None) -> str:
        """Reset Kubernetes Resource Version to 0 in Airflow Metadata DB"""
        session.query(KubeResourceVersion).update({
            KubeResourceVersion.resource_version: '0'
        })
        session.commit()
        return '0'


class KubeWorkerIdentifier(Base):
    """Table containing Kubernetes Worker Identified"""

    __tablename__ = "kube_worker_uuid"
    one_row_id = Column(Boolean, server_default=sqltrue(), primary_key=True)
    worker_uuid = Column(String(255))

    @staticmethod
    @provide_session
    def get_or_create_current_kube_worker_uuid(session: Session = None) -> str:
        """Create & Store Worker UUID in DB if it doesn't exists in DB, retrieve otherwise"""
        (worker_uuid,) = session.query(KubeWorkerIdentifier.worker_uuid).one()
        if worker_uuid == '':
            worker_uuid = str(uuid.uuid4())
            KubeWorkerIdentifier.checkpoint_kube_worker_uuid(worker_uuid, session)
        return worker_uuid

    @staticmethod
    @provide_session
    def checkpoint_kube_worker_uuid(worker_uuid: str, session: Session = None) -> None:
        """Update the Kubernetes Worker UUID in the DB"""
        if worker_uuid:
            session.query(KubeWorkerIdentifier).update({
                KubeWorkerIdentifier.worker_uuid: worker_uuid
            })
            session.commit()
