from .logexception import LogException


def copy_project(from_client, to_client, from_project, to_project):
    """
    copy project, logstore, machine group and logtail config to target project,
    expecting the target project doens't exist
    :type from_client: logclient
    :param from_project: logclient instance

    :type to_client: logclient
    :param to_client: logclient instance

    :type from_project: string
    :param from_project: project name

    :type to_project: string
    :param to_project: project name
    :return:
    """

    # copy project
    ret = from_client.get_project(from_project)
    ret = to_client.create_project(to_project, ret.get_description())

    # list logstore and copy them
    offset, size = 0, 100
    while True:
        ret = from_client.list_logstore(from_project, offset=offset, size=size)
        count = ret.get_logstores_count()
        for logstore_name in ret.get_logstores():
            # copy logstore
            ret = from_client.get_logstore(from_project, logstore_name)
            ret = to_client.create_logstore(to_project, logstore_name, ret.get_ttl(), ret.get_shard_count())

            # copy index
            try:
                ret = from_client.get_index_config(from_project, logstore_name)
                ret = to_client.create_index(to_project, logstore_name, ret.get_index_config())
            except LogException as ex:
                if ex.get_error_code() == 'IndexConfigNotExist':
                    pass

        if count < size:
            break

    # list logtail config and copy them
    offset, size = 0, 100
    while True:
        ret = from_client.list_logtail_config(from_project, offset=offset, size=size)
        count = ret.get_configs_count()

        for config_name in ret.get_configs():
            ret = from_client.get_logtail_config(from_project, config_name)
            ret = to_client.create_logtail_config(to_project, ret.logtail_config)

        if count < size:
            break

    # list machine group and copy them
    offset, size = 0, 100
    while True:
        ret = from_client.list_machine_group(from_project, offset=offset, size=size)
        count = ret.get_machine_group_count()

        for group_name in ret.get_machine_group():
            ret = from_client.get_machine_group(from_project, group_name)
            ret = to_client.create_machine_group(to_project, ret.get_machine_group())

            # list all applied config and copy the relationship
            ret = from_client.get_machine_group_applied_configs(from_project, group_name)
            for config_name in ret.get_configs():
                to_client.apply_config_to_machine_group(to_project, config_name, group_name)

        if count < size:
            break

