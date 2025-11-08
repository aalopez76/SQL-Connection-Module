def test_imports():
    import sql_connection
    from sql_connection import get_connector
    assert callable(get_connector)
