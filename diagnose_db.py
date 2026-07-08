import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="DATAi2i_db",
    user="postgres",
    password="Manoj@2005"
)
cur = conn.cursor()

# Check columns for the tables we need
for table in ["stores", "sales", "reports", "districts", "regions", "roles"]:
    print(f"\n📐 Columns in '{table}':")
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s AND table_schema = 'public'
        ORDER BY ordinal_position;
    """, (table,))
    cols = cur.fetchall()
    if cols:
        for c in cols:
            print(f"  - {c[0]} ({c[1]})")
        
        # Show sample row
        cur.execute(f"SELECT * FROM {table} LIMIT 1;")
        row = cur.fetchone()
        if row:
            col_names = [desc[0] for desc in cur.description]
            print(f"  Sample: {dict(zip(col_names, row))}")
    else:
        print("  (table not found or empty)")

cur.close()
conn.close()
print("\n✅ Done")
