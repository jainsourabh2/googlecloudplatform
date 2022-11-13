# Create a Machine Learning Model using ARIMA_PLUS
# The data_frequency is set to AUTO_FREQUENCY.
# Please select the option appropriately from https://cloud.google.com/bigquery-ml/docs/reference/standard-sql/bigqueryml-syntax-create-time-series#create_model_syntax
# Replace the values approrpiately for
# <<project-id>>
# <<dataset-id>>
# <<table-id>>
# <<model-id>>

CREATE OR REPLACE MODEL
  <<dataset-id>>.<<model-id>> OPTIONS ( 
    model_type='ARIMA_PLUS',
    auto_arima=TRUE,
    data_frequency='AUTO_FREQUENCY',
    time_series_data_col = 'originhits',
    time_series_timestamp_col = 'dt',
    time_series_id_col = 'cpcode'
    ) 
AS 
(
  SELECT
    PARSE_TIMESTAMP("%Y-%m-%d", CAST(dt AS STRING)) AS dt,
    SUM(originhits) AS originhits,
    cpcode
  FROM
    `<<project-id>>.<<dataset-id>>.<<table-id>>`
  GROUP BY
    dt,
    cpcode 
);

# Forecast based on the model.
# You can specify the duration as the horizon. 
# The frequency is based on the model creation value of data_frequency

SELECT
  *
FROM
  ML.FORECAST(MODEL <<dataset-id>>.<<table-id>>,
    STRUCT(30 AS horizon,
      0.9 AS confidence_level));

#Fetch the coeffecints for the model

SELECT
  *
FROM
  ML.ARIMA_COEFFICIENTS(MODEL <<dataset-id>>.<<model-id>>);

#Sample Query for forecasting and perforning a union with the historical data.

SELECT
  date,
  history_value AS history_value,
  NULL AS forecast_value,
  cpcode,
  NULL AS prediction_interval_lower_bound,
  NULL AS prediction_interval_upper_bound
FROM (
  SELECT
    PARSE_TIMESTAMP("%Y-%m-%d", CAST(dt AS STRING)) AS date,
    SUM(originhits) AS history_value,
    CAST(cpcode AS INT64) AS cpcode
  FROM
    `<<project-id>>.<<dataset-id>>.<<table-id>>`
  GROUP BY
    date,
    cpcode
  ORDER BY
    date,
    cpcode ASC )
UNION ALL
SELECT
  forecast_timestamp AS date,
  NULL AS history_value,
  forecast_value AS forecast_value,
  cpcode,
  prediction_interval_lower_bound,
  prediction_interval_upper_bound
FROM
  ML.FORECAST(MODEL `<<project-id>>.<<dataset-id>>.<<model-id>>`,
    STRUCT(30 AS horizon,
      0.9 AS confidence_level));

SELECT
  *
FROM
  ML.DETECT_ANOMALIES(MODEL `<<project-id>>.<<dataset-id>>.<<model-id>>`,
    STRUCT(0.95 AS anomaly_prob_threshold))
WHERE
  is_anomaly = TRUE;
