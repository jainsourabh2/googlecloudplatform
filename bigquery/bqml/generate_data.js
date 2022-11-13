/*
Generate sample data for CDN data for Machine Learning Demonstration.
Using ARIMA_PLUS model to predict the number of originhits, edgehits and offlinehits.
Also the models helps to predict Anomalies.
"dt","startdatetime","cpcode","response_code","originhits","originbytes","edgehits","edgebytes","offloadhits","offloadbytes","startdatetimeist"
"2022-10-21","2022-10-21 11:30:00",1367469,503,66632757,415805,147,500670,55.2631578947368,54.6299680782749,"2022-10-21 17:00:00"
*/

var fs = require('fs');

//Sample cp_code values against which the model can be created.
var cp_code = [1069770,1367469,1236405,1136019,1136008,1069518,1277305,1274090,1274089,1274086,1136022,1136001,1135952,1136039,1136038,1136024,1136023,1136021,1136018,1308083,1277307,1277306,1274091]

//Sample response code values.
var resp_code = [0,304,400,403,404,200,204,206,500,502,503,504]

//Start Date from which the data needs to be generated.
var start_date = new Date('2022-01-01');

//Header values for the generated data.
console.log('"dt","startdatetime","cpcode","response_code","originhits"');

//Loop to generate random values for the CDN data.
for (let i = 1; i < 366; i++) {
	let dt_format = start_date.toISOString().split('T')[0]
	for (let j = 0; j < cp_code.length; j++) {
		let cp_code_output = cp_code[Math.floor(Math.random() * cp_code.length)]
		let resp_code_output = resp_code[Math.floor(Math.random() * resp_code.length)]
		let origin_hits = Math.floor((Math.random() * (5000*i - 1) + 1));
  		console.log(dt_format +","+start_date.toISOString().split(' ')+","+cp_code_output+","+resp_code_output+","+origin_hits)
	}
  	start_date.setDate(start_date.getDate() + 1);
}
