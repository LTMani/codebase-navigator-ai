package com.navigator.ledger

import org.apache.spark.sql.{Dataset, SparkSession}
import org.apache.spark.sql.functions._
import java.sql.Timestamp

object LedgerReconciliationJob {

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("FintechLedgerReconciliation")
      .master("local[*]")
      .getOrCreate()

    import spark.implicits._

    val inputPath = if (args.nonEmpty) args(0) else "data/journal_entries.parquet"
    val outputPath = if (args.length > 1) args(1) else "data/reconciliation_results.parquet"

    println(s"Starting Ledger Reconciliation Job on input: $inputPath")

    val df = spark.read.parquet(inputPath)

    val reconciled = df.groupBy("accountId")
      .agg(
        sum(when($"entryType" === "Credit", $"amount").otherwise(-$"amount")).as("netCalculatedBalance"),
        count("*").as("totalEntries")
      )
      .withColumn("reconciledAt", current_timestamp())

    reconciled.write.mode("overwrite").parquet(outputPath)

    println(s"Completed reconciliation output to: $outputPath")
    spark.stop()
  }
}
