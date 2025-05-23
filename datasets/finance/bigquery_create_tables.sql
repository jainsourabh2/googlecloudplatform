CREATE TABLE `cloud-demos-gcp.fin_data.dim_date` (
  `date_key` INT64 OPTIONS(description="Unique key for each date (YYYYMMDD)"),
  `date` STRING OPTIONS(description="Full calendar date"),
  `day` INT64 OPTIONS(description="Day of the month"),
  `month` INT64 OPTIONS(description="Month number"),
  `quarter` STRING OPTIONS(description="Quarter of the year"),
  `year` INT64 OPTIONS(description="Year"),
  `is_weekend` BOOL OPTIONS(description="Indicates if the date is a weekend")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_customer` (
  `customer_id` STRING OPTIONS(description="Unique identifier for the customer"),
  `name` STRING OPTIONS(description="Name of the customer"),
  `segment` STRING OPTIONS(description="Customer segment type")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_account` (
  `account_id` STRING OPTIONS(description="Unique identifier for the account"),
  `type` STRING OPTIONS(description="Type of the account (e.g., Savings, Checking)")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_branch` (
  `branch_id` STRING OPTIONS(description="Unique identifier for the branch"),
  `city` STRING OPTIONS(description="City where the branch is located")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_product` (
  `product_id` STRING OPTIONS(description="Unique identifier for the product"),
  `name` STRING OPTIONS(description="Name of the financial product"),
  `category` STRING OPTIONS(description="Category of the product")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_transaction_type` (
  `transaction_type_id` STRING OPTIONS(description="Unique identifier for the transaction type"),
  `description` STRING OPTIONS(description="Description of the transaction type")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_currency` (
  `currency_id` STRING OPTIONS(description="Unique identifier for the currency"),
  `code` STRING OPTIONS(description="Currency code (e.g., USD, EUR)")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_channel` (
  `channel_id` STRING OPTIONS(description="Unique identifier for the channel"),
  `name` STRING OPTIONS(description="Channel name (e.g., Mobile, Web)")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_region` (
  `region_id` STRING OPTIONS(description="Unique identifier for the region"),
  `name` STRING OPTIONS(description="Name of the region")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_employee` (
  `employee_id` STRING OPTIONS(description="Unique identifier for the employee"),
  `name` STRING OPTIONS(description="Name of the employee")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_risk_score` (
  `risk_score_id` STRING OPTIONS(description="Unique identifier for the risk score"),
  `level` STRING OPTIONS(description="Risk level description")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_merchant` (
  `merchant_id` STRING OPTIONS(description="Unique identifier for the merchant"),
  `name` STRING OPTIONS(description="Name of the merchant")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_loan_type` (
  `loan_type_id` STRING OPTIONS(description="Unique identifier for the loan type"),
  `type` STRING OPTIONS(description="Type of loan (e.g., Personal, Auto)")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_fraud_status` (
  `fraud_status_id` STRING OPTIONS(description="Unique identifier for fraud status"),
  `status` STRING OPTIONS(description="Fraud status description")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_payment_mode` (
  `payment_mode_id` STRING OPTIONS(description="Unique identifier for payment mode"),
  `mode` STRING OPTIONS(description="Payment mode description")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_time` (
  `time_id` STRING OPTIONS(description="Unique identifier for time"),
  `hour` INT64 OPTIONS(description="Hour of the day (0-23)")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_tax_code` (
  `tax_code_id` STRING OPTIONS(description="Unique identifier for tax code"),
  `code` STRING OPTIONS(description="Tax code")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_credit_rating` (
  `credit_rating_id` STRING OPTIONS(description="Unique identifier for credit rating"),
  `rating` STRING OPTIONS(description="Credit rating value")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_investment_plan` (
  `investment_plan_id` STRING OPTIONS(description="Unique identifier for investment plan"),
  `plan` STRING OPTIONS(description="Investment plan name")
);

CREATE TABLE `cloud-demos-gcp.fin_data.dim_policy` (
  `policy_id` STRING OPTIONS(description="Unique identifier for policy"),
  `policy_name` STRING OPTIONS(description="Name of the policy")
);

CREATE TABLE `cloud-demos-gcp.fin_data.fact_financial_transactions` (
  `transaction_id` STRING OPTIONS(description="Unique identifier for the transaction"),
  `transaction_date_key` INT64 OPTIONS(description="Date key of the transaction (YYYYMMDD)"),
  `customer_id` STRING OPTIONS(description="Foreign key to customer"),
  `account_id` STRING OPTIONS(description="Foreign key to account"),
  `product_id` STRING OPTIONS(description="Foreign key to product"),
  `branch_id` STRING OPTIONS(description="Foreign key to branch"),
  `transaction_type_id` STRING OPTIONS(description="Foreign key to transaction type"),
  `currency_id` STRING OPTIONS(description="Foreign key to currency"),
  `channel_id` STRING OPTIONS(description="Foreign key to channel"),
  `region_id` STRING OPTIONS(description="Foreign key to region"),
  `employee_id` STRING OPTIONS(description="Foreign key to employee"),
  `risk_score_id` STRING OPTIONS(description="Foreign key to risk score"),
  `merchant_id` STRING OPTIONS(description="Foreign key to merchant"),
  `loan_type_id` STRING OPTIONS(description="Foreign key to loan type"),
  `fraud_status_id` STRING OPTIONS(description="Foreign key to fraud status"),
  `payment_mode_id` STRING OPTIONS(description="Foreign key to payment mode"),
  `time_id` STRING OPTIONS(description="Foreign key to time"),
  `tax_code_id` STRING OPTIONS(description="Foreign key to tax code"),
  `credit_rating_id` STRING OPTIONS(description="Foreign key to credit rating"),
  `investment_plan_id` STRING OPTIONS(description="Foreign key to investment plan"),
  `policy_id` STRING OPTIONS(description="Foreign key to policy"),
  `amount` FLOAT64 OPTIONS(description="Transaction amount")
);