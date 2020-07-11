from oslo_concurrency import lockutils
from oslo_db.sqlalchemy import enginefacade

_synchronized = lockutils.synchronized_with_prefix("cloudmonitor-")
_CTX_MANAGER = None


@_synchronized("context-manager")
def _create_context_manager():
    global _CTX_MANAGER
    if _CTX_MANAGER is None:
        _CTX_MANAGER = enginefacade.transaction_context()
        _CTX_MANAGER.configure(sqlite_fk=True, flush_on_subtransaction=True)

    return _CTX_MANAGER


def get_context_manager():
    """Transaction Context Manager accessor.

    :returns: The transaction context manager.
    """
    if _CTX_MANAGER is None:
        return _create_context_manager()

    return _CTX_MANAGER


def get_reader_session():
    """Helper to get reader session.

    :returns: The reader session.
    """
    return get_context_manager().reader.get_sessionmaker()()


def get_writer_session():
    """Helper to get writer session.

    :returns: The writer session.
    """
    return get_context_manager().writer.get_sessionmaker()()
