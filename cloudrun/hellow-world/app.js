
const express = require('express');
const app = express();

app.get('/', async (req, res) => {
  res.send('Welcome to Hello World');
});

const port = parseInt(process.env.PORT) || 3000;
app.listen(port, () => {
  console.log(`helloworld: listening on port ${port}`);
});
