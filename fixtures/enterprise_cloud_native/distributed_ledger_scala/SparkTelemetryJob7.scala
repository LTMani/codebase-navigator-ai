package com.navigator.analytics.spark.job7

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import java.sql.Timestamp

case class TelemetryRecord7(
    recordId: String,
    tenantId: String,
    metricValue: Double,
    recordedAt: Timestamp
)

object SparkTelemetryJob7 {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("SparkTelemetryPipeline_7")
      .master("local[*]")
      .getOrCreate()

    import spark.implicits._

    val inputPath = if (args.nonEmpty) args(0) else "data/telemetry_input_7.parquet"
    val df = spark.read.parquet(inputPath)

    val aggregated = df.groupBy("tenantId")
      .agg(
        avg("metricValue").as("averageMetric"),
        count("*").as("totalEvents")
      )

    aggregated.write.mode("overwrite").parquet("data/telemetry_output_7.parquet")
    spark.stop()
  }
}
