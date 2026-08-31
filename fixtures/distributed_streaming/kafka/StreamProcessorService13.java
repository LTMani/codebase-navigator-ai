package com.navigator.streaming.service13;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.kstream.*;
import lombok.extern.slf4j.Slf4j;
import java.time.Duration;
import java.util.Properties;

@Slf4j
public class StreamProcessorService13 {

    private final String inputTopic = "telemetry.events.stream13";
    private final String outputTopic = "telemetry.aggregated.stream13";
    private final Properties config = new Properties();

    public StreamProcessorService13(String bootstrapServers) {
        config.put(StreamsConfig.APPLICATION_ID_CONFIG, "navigator-stream-proc-13");
        config.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        config.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass().getName());
        config.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass().getName());
        config.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 1000);
    }

    public KafkaStreams buildTopology() {
        StreamsBuilder builder = new StreamsBuilder();
        KStream<String, String> stream = builder.stream(inputTopic);

        KTable<Windowed<String>, Long> aggregated = stream
                .filter((key, value) -> value != null && !value.isEmpty())
                .mapValues(String::toUpperCase)
                .groupByKey()
                .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(5)))
                .count(Materialized.as("aggregated-count-store"));

        aggregated.toStream()
                .map((key, value) -> new KeyValue<>(key.key(), String.valueOf(value)))
                .to(outputTopic, Produced.with(Serdes.String(), Serdes.String()));

        return new KafkaStreams(builder.build(), config);
    }
}
