using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Data.SqlClient;
using System.Data;
using System.ComponentModel;

namespace SQLLib
{
    public class SQLUtils : IDisposable
    {
        // The SQL Connection string
        SqlConnection conn;

        public SQLUtils(string connstr)
        {
            conn = new SqlConnection(connstr);
        }

        ~SQLUtils()
        {
            Dispose();
        }

        public void GetTableFromQuery(string query, DataTable dtResult)
        {
            // create data adapter
            SqlDataAdapter da = new SqlDataAdapter(query, conn);

            // this will query your database and return the result to your datatable
            try
            {
                da.Fill(dtResult);
            }
            finally
            {
                da.Dispose();
            }
        }

        public void Dispose()
        {
            if (conn.State == System.Data.ConnectionState.Open)
                conn.Close();

            conn.Dispose();
        }

        public void BulkInsert<T>(string tableName, IList<T> list)
        {
            using (var bulkCopy = new SqlBulkCopy(conn))
            {
                OpenConnecion();

                bulkCopy.BatchSize = list.Count;
                bulkCopy.DestinationTableName = tableName;

                var table = new DataTable();
                var props = TypeDescriptor.GetProperties(typeof(T))
                    //Dirty hack to make sure we only have system data types 
                    //i.e. filter out the relationships/collections
                                           .Cast<PropertyDescriptor>()
                                           .Where(propertyInfo => propertyInfo.PropertyType.Namespace.Equals("System"))
                                           .ToArray();

                foreach (var propertyInfo in props)
                {
                    bulkCopy.ColumnMappings.Add(propertyInfo.Name, propertyInfo.Name);
                    table.Columns.Add(propertyInfo.Name, Nullable.GetUnderlyingType(propertyInfo.PropertyType) ?? propertyInfo.PropertyType);
                }

                var values = new object[props.Length];
                foreach (var item in list)
                {
                    for (var i = 0; i < values.Length; i++)
                    {
                        values[i] = props[i].GetValue(item);
                    }

                    table.Rows.Add(values);
                }

                bulkCopy.WriteToServer(table);
            }
        }

        public void RunCommand(string queryString)
        {
            OpenConnecion();

            SqlCommand command = new SqlCommand(queryString, conn);

            command.ExecuteNonQuery();
        }

        private void OpenConnecion()
        {
            if (conn.State == ConnectionState.Closed)
                conn.Open();
        }
    }
}
