# QBUS3850 Group Assignment

## Summary

The assignment consists of identification of a dataset that is suitable for forecasting and posterior decision-making on the forecasts (i.e. having accurate forecast can produce some form of benefit), finding good forecasting models to forecast the dataset (including validation and evaluation) and reporting a discussion and conclusions of impact of the forecasting models, limitations or tradeoffs.

## Group sizes

Groups of 5 students.

## Dataset and Business Application

You will find a dataset of time series that are suitable to forecast from the statistical point of view and has some 'business application'. You can be creative on the application, use your knowledge of statistical principles to justify how having forecasts can be beneficial in a business context, it does not need to be one of the typical scenarios. The business logic/impact can be made from the point of view of how a business can benefit from point forecasts, prediction quantiles or prediction intervals, or even the full distribution.

### Dataset Requirements

- Recommended at least 3 'cycles'. Usually 3 (or more) years of history will be enough for all frequencies, but if you want to analyze weekly data or higher frequencies, you can use less timepoints (e.g. less than 3 years of weekly data), *as long as the problem of potential yearly seasonality that cannot be analyzed is properly dealt with*.
- Numerical data, if the data is heavily non-smooth / non-'gaussian-like', such as count data or binary, proper transformations or other ways of making it suitable for the application of the classic model families seen in class must be justified.
- A minimum of 10 time series of the same nature (e.g. similar data types like inflation). It is a minimum; more than 10 series are recommended.
- Forecast horizon: Consider the timeframe for the forecasts, *both short horizon and long horizon*, with a justification of what is considered short and long.
- Suitable to apply performance metrics. This includes forecast accuracy metrics, but can also include performance metrics related to the business logic (that you would create based on your judgement).

### Dataset Interestingness **(15% of the total grade)**

The chosen dataset has to exhibit *some* of the properties that lead to an interesting question, i.e. require some complex analysis, outside of "straightforward application of ARIMA/Exponential Smoothing + model selection by AIC". Some aspects of it are suggested below, you do not need to cover all!

- **Seasonality**, including potential stochasticity in the seasonal patterns, like changes over time or exhibits some noise within the same periodicity, or time series that have different frequencies across the dataset, forcing you to create a method to find the frequency per dataset.
- **Frequency Dynamics.** For example, a dataset that is measured in daily frequency or higher (high frequency), that when aggregated temporally to monthly or lower (low frequency), it is still interesting from the forecasting point of view. You would analyze both aspects if you go for this interesting feature. *Temporal aggregation can be achieved by taking the time series of daily measurements and creating the time series of 'averaged daily measurements' per month (or from any lower frequency to any higher frequency).*
- **Heteroskedasticity** (beyond transformations like log, or multiplicative seasonality), so the ARCH/GARCH methods can have some impact (though can be secondary). This can be time series for which the dynamic variance is of interest, so ARCH/GARCH can be applied, or just indirectly applied to improve some forecast matric.
- **VAR:** Series is suitable for VAR models, some interactions. The dataset would then be multivariate series. For example, if you choose a pair of series, this means that the minimum number of 10 multivariate time series: 10 sets of 2 time series.
- **Exogenous predictors:** There are some external data that can be used, the exogenous variables should be available ahead of time (know the value, like a holiday effect or a sales).
- **'Exotic' data types** like count or binary data, but remember to do a proper justification of how to approach this datatype with the classic models that assume distributions close to Gaussian.
- **Hierarchical time series:** The time series form a coherent set of that can be aggregated cross-sectionally. Like tourism arrivals in each region in a country, which then all regions are summed up and the total arrival in a country is also of interest; sales/revenue of a supermarket chain that can be then aggregated by zone or product type. If the that has this property, it would also be analyzed (such as compared performance of individual series forecasts aggregated, vs forecast on the aggregated series).

### Relevant business problem **(10% of the total grade)**

Justification of the business context and what type of forecast is needed. Type of forecast as in Point forecast, Quantile or Prediction Intervals, or Scenario analysis from simulations of forecasts paths. This includes an explanation of the source dataset, and what it means.

## Exploratory Data Analysis and Suitability Report **(15% of the total grade)**

Analyze the dataset for quality issues like

- Poor quality for the oldest forecasts
- Noticeable structural breaks (change of pattern like jump or changes in the dynamics)
- Missingness
- Outliers

Pre-processing

- Cleaning
- Imputation
- Transformations

Analysis and Justification of the suitability and 'interestingness' properties: you might use decomposition plots or simpler application of models so see if they exhibit the claimed property,

## Forecast Methodology

You will come up with 3 categories of models: (1) A simple, explainable model, (2) a maximum performance model (3) A 'new', innovative model outside of the model families that we have covered in the unit.

The methodology has to be automatic, you can analyze a few series manually, but overall, it needs to be applied to all time series without human interaction once the methodology is settled. For example, imagine that you need to forecast a large set of time series (millions!) and you cannot afford to analyze each one individually, so you would propose a set of potential good models along with a model selection criterion, based on a subset that you analyze carefully to derive your criterion.

### The simplest, explainable competitive model **(10% of the total grade)**

You will find a model that is explainable, like exponential smoothing with proper understanding of estimated parameter values, forecast patterns; ARIMA with a low order. It can even be a non-time series model like 'linear regression' based on a historic linear trend, historic mean or something else. This model needs to be validated: it needs to be justified vs a set of other explainable models. Decisions can be made on the basis of performance metrics but can have a subjective component of explainability.

### The maximum performance model **(20% of the total grade)**

This would be a methodology that optimizes for performance, including model selection from a range of model classes, model combination. It can consider aspects like model complexity vs data availability.

### The creative model **(10% of the total grade)**

You will come up with a 'new' model that is not a simple application of the classic model families that we have studied in class, standard transformations like Box-Cox or combinations. Some ideas:

- Sophisticated nonstandard transformations that require insights from the data.
- Composition like using a different model for the residuals coming from another model
- Nonlinear model in autoregressive form such as a decision tree based on the past few observations.
- Models that you can find implemented in python. This has to come with a proper justification of why this model is suitable for your problem

The creative model does not need to be 'peak' performance, but it needs a justification in terms of what capabilities this new model can have with respect to the other two methodologies.

### Metrics and Validation Setup

Design a performance criterion to compare models and report later on, together with a validation (like temporal holdout). It has to be justified with the business logic and applied in the forecast methodology section.

Some ideas for criteria of performance that match the business context:

- Classic measures of prediction error (MAE, MSE, MAPE)
- Bias (systematic over forecasting or under forecasting)
- Others like risk of extreme values etc.,
- Comparison of performance per horizon
- Percentage of wins vs a benchmark model
- Directional accuracy in predicting up or down trend)
- *Recommended: Metrics that are non-standard (outside of MAE/ MSE / MAPE) to capture business logic benefits (this could be creative).*

## Conclusions **(10% of the total grade)**

- Report on your findings in impact of your results in plain, nonstatistical language
- Report of Expected Performance (when the model is run in the real world after this exercise), including relative tradeoffs vs using a simple model
- Limitations of the model, including possible patterns in the data that are not solvable with the given models, how would you improve the model if you had more time to work on it and as it gets more data over time (or potential data sources).

## Visual Presentation **(10% of the total grade)**

- Clarity and Succinctness in the explanations and report.
- Visual quality and readability of the figures and tables.

## Deliverables

1. **A report in pdf format.** Maximum of **15** pages. Title, List of references, etc. Do not count, but no Appendix, *all content has to be within the 15 pages.* Focus on including the key messages. A suggestion of structure:
   - **Executive Summary (1 page):** What is the problem, what data was used, which models won, and what is the business value based on your 'business logic' criterion.
   - **Dataset & Business Context (1-2 pages):** Justify the dataset's relevance and explain the forecasting goal.
   - **EDA & Preprocessing (3 pages max):** Focus only on the anomalies, and exploration of stylized facts (trend, seasons, dynamic volatility, etc.) that actually influenced modeling decisions.
   - **Methodology & Modeling (5-7 pages):** Explain the Simple, Max Performance, and Creative models. How do you set the
   - **Validation & Results (2 pages):** Performance metrics and comparisons.
   - **Conclusions, Impact & Limitations (1-2 pages):** What is the value of your approach, what is not perfect and what would you do to improve your solution even further.

2. **A jupyter notebook that reproduces the results of the report.** It needs to run when "Run all cells" from a clean environment. **Failure to run will result in a multiplicative penalty of x0.95 for minor problems (like not finding the dataset file because of the path is set to absolute in your computer, instead of in the same folder as the notebook). Major penalties if the notebook does not match the report.**

3. **A .csv dataset that the notebook uses.** Assuming it is in the same folder of the report.

4. **An admin log:** It is recommended that the group maintain an admin log with an outline of each member's contribution and a summary of the meetings. *It is not required to submit but might be requested in case of conflicts.*

## Grade Breakdown Summary

| Component | Weight |
|---|---|
| Dataset Interestingness | 15% |
| Relevant Business Problem | 10% |
| EDA & Suitability Report | 15% |
| Simplest Explainable Model | 10% |
| Maximum Performance Model | 20% |
| Creative Model | 10% |
| Conclusions | 10% |
| Visual Presentation | 10% |
| **Total** | **100%** |
