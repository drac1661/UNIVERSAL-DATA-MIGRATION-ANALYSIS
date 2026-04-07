import extractor.allTableExtractor as allTableExtractor

def main():
    with allTableExtractor.AllTableExtractor() as extractor:
        # Get user-defined schemas
        schemas = extractor.get_all_user_schemas()
        print(f"Found schemas: {schemas}\n")
        
        # Get all tables with their info
        tables_info = extractor.get_all_tables_with_schemas()
        
        if not tables_info:
            print("No tables found in the database.")
            return
        
        print(f"Found {len(tables_info)} tables:\n")
        
        for table_key, info in tables_info.items():
            print(f"Table: {table_key}")
            print(f"  Schema: {info['schema']}")
            print(f"  Columns: {len(info['columns'])} columns")
            for col in info['columns']:
                print(f"    - {col['name']}: {col['type']}")
            print(f"  Primary Keys: {info['primary_keys']}")
            print(f"  Foreign Keys: {len(info['foreign_keys'])} relationships")
            print("-" * 60)

if __name__ == "__main__":
    main()