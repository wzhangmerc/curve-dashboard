import snowflake.connector

def get_connection():
    return snowflake.connector.connect(
        user='WZHANG@MERCURIA.COM',
        account='mercuria-fotech',  # This comes from your Server
        warehouse='FREIGHT',
        role='SNOWFLAKE_SPGPLATTS',
        authenticator='externalbrowser'
    )
