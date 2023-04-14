package com.google.cloud.demo.model;

public class LogMessage {

  public static class RequestPayload {
    int userId;
    String action;

    public RequestPayload(int userId, String action) {
      this.userId = userId;
      this.action = action;
    }

    public RequestPayload(Builder builder) {
      this.userId = builder.userId;
      this.action = builder.action;
    }

    public static class Builder {
      int userId;
      String action;

      public Builder setUserId(int userId) {
        this.userId = userId;
        return this;
      }

      public Builder setAction(String action) {
        this.action = action;
        return this;
      }

      public RequestPayload build() {
        return new RequestPayload(this);
      }
    }

  }

  String timestamp;
  String requestId;
  int responseTime;
  String requestMethod;
  String requestUrl;
  int responseCode;
  String responseMessage;
  RequestPayload requestPayload;
  String serverIP;
  String userAgent;

  public LogMessage(String timestamp, String requestId, int responseTime, String requestMethod, String requestUrl,
      int responseCode, String responseMessage, RequestPayload requestPayload, String serverIP, String userAgent) {
    this.timestamp = timestamp;
    this.requestId = requestId;
    this.responseTime = responseTime;
    this.requestMethod = requestMethod;
    this.requestUrl = requestUrl;
    this.responseCode = responseCode;
    this.responseMessage = responseMessage;
    this.requestPayload = requestPayload;
    this.serverIP = serverIP;
    this.userAgent = userAgent;
  }

  public LogMessage(Builder builder) {
    this.timestamp = builder.timestamp;
    this.requestId = builder.requestId;
    this.responseTime = builder.responseTime;
    this.requestMethod = builder.requestMethod;
    this.responseCode = builder.responseCode;
    this.responseMessage = builder.responseMessage;
    this.requestPayload = builder.requestPayload;
    this.serverIP = builder.serverIP;
    this.userAgent = builder.userAgent;
  }

  public static class Builder {

    String timestamp;
    String requestId;
    int responseTime;
    String requestMethod;
    String requestUrl;
    int responseCode;
    String responseMessage;
    RequestPayload requestPayload;
    String serverIP;
    String userAgent;

    public Builder setTimestamp(String timestamp) {
      this.timestamp = timestamp;
      return this;
    }

    public Builder setRequestId(String requestId) {
      this.requestId = requestId;
      return this;
    }

    public Builder setResponseTime(int responseTime) {
      this.responseTime = responseTime;
      return this;
    }

    public Builder setRequestMethod(String requestMethod) {
      this.requestMethod = requestMethod;
      return this;
    }

    public Builder setRequestUrl(String requestUrl) {
      this.requestUrl = requestUrl;
      return this;
    }

    public Builder setResponseCode(int responseCode) {
      this.responseCode = responseCode;
      return this;
    }

    public Builder setResponseMessage(String responseMessage) {
      this.responseMessage = responseMessage;
      return this;
    }

    public Builder setRequestPayload(RequestPayload requestPayload) {
      this.requestPayload = requestPayload;
      return this;
    }

    public Builder setServerIP(String serverIP) {
      this.serverIP = serverIP;
      return this;
    }

    public Builder setUserAgent(String userAgent) {
      this.userAgent = userAgent;
      return this;
    }

    public LogMessage build() {
      return new LogMessage(this);
    }
  }
}
