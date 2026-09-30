package com.astromeric.android.core.model

import com.google.gson.TypeAdapter
import com.google.gson.stream.JsonReader
import com.google.gson.stream.JsonToken
import com.google.gson.stream.JsonWriter

/**
 * Reads a list of strings that the server may send either as a JSON array or as
 * one comma-separated string. The Moon ritual's "avoid" moved from a list to
 * `"Starting new ventures, Making impulsive decisions"`, and a plain
 * `List<String>` field fails on the whole response when it meets a string.
 */
class StringOrListAdapter : TypeAdapter<List<String>>() {
    override fun write(out: JsonWriter, value: List<String>?) {
        if (value == null) {
            out.nullValue()
            return
        }
        out.beginArray()
        value.forEach { out.value(it) }
        out.endArray()
    }

    override fun read(reader: JsonReader): List<String> =
        when (reader.peek()) {
            JsonToken.NULL -> {
                reader.nextNull()
                emptyList()
            }
            JsonToken.STRING ->
                reader.nextString().split(",").map { it.trim() }.filter { it.isNotEmpty() }
            JsonToken.BEGIN_ARRAY -> {
                val items = mutableListOf<String>()
                reader.beginArray()
                while (reader.hasNext()) {
                    if (reader.peek() == JsonToken.NULL) reader.nextNull() else items += reader.nextString()
                }
                reader.endArray()
                items
            }
            else -> {
                reader.skipValue()
                emptyList()
            }
        }
}
