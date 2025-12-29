"""Display database schema."""
from sqlalchemy import inspect, create_engine

engine = create_engine('sqlite:///bot_database.db')
inspector = inspect(engine)
tables = inspector.get_table_names()

print('\n' + '='*60)
print('       DATABASE SCHEMA (bot_database.db)')
print('='*60)

for table in tables:
    print(f'\n📋 TABLE: {table.upper()}')
    print('-'*60)
    
    columns = inspector.get_columns(table)
    for col in columns:
        pk = ' [PRIMARY KEY]' if col.get('primary_key') else ''
        nullable = ' NULL' if col.get('nullable') else ' NOT NULL'
        print(f'  • {col["name"]:25} {str(col["type"]):20}{nullable}{pk}')

print('\n' + '='*60)
print('Total tables:', len(tables))
print('='*60 + '\n')
