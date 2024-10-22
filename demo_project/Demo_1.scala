// Import necessary Spark libraries
import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.functions._

object Demo_1 {
  def main(args: Array[String]): Unit = {
    // Check if arguments are provided
    if (args.length < 1) {
      System.err.println("Usage: Demo_1 <input_file_path>")
      System.exit(1)
    }

    // Parse input file path from arguments
    val inputFilePath = args(0)

    // Create a Spark session
    val spark = SparkSession.builder
      .appName("Demo_1 Spark Job")
      .getOrCreate()

    // Read input data (CSV file in this case)
    val inputDF: DataFrame = spark.read
      .option("header", "true")
      .csv(inputFilePath)

    // Perform a simple transformation (filter rows where a certain column value is not null)
    val filteredDF = inputDF.filter(col("some_column").isNotNull)

    // Show the result (for demonstration purposes)
    filteredDF.show()

    // Stop the Spark session
    spark.stop()
  }
}
