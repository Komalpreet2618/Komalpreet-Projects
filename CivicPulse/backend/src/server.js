require("dotenv").config();

const app = require("./app");
const pool = require("./config/db");

const PORT = process.env.PORT || 5000;

pool
  .query(`
    SELECT
      current_database() AS database_name,
      version() AS postgres_version,
      PostGIS_Version() AS postgis_version
  `)
  .then((result) => {
    console.log("PostgreSQL connected successfully!");
    console.log("Database:", result.rows[0].database_name);
    console.log("PostGIS version:", result.rows[0].postgis_version);

    app.listen(PORT, () => {
      console.log(`CivicPulse backend running on port ${PORT}`);
    });
  })
  .catch((error) => {
    console.error("Failed to connect to PostgreSQL:", error.message);
    process.exit(1);
  });