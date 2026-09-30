const pool = require("../config/db");

const createIssueImage = async (issueId, imageUrl) => {
  const query = `
    INSERT INTO issue_images (
      issue_id,
      image_url
    )
    VALUES ($1, $2)
    RETURNING *;
  `;

  const result = await pool.query(query, [
    issueId,
    imageUrl,
  ]);

  return result.rows[0];
};

const getIssueImages = async (issueId) => {
  const query = `
    SELECT
      id,
      issue_id,
      image_url,
      uploaded_at
    FROM issue_images
    WHERE issue_id = $1
    ORDER BY uploaded_at ASC;
  `;

  const result = await pool.query(query, [issueId]);

  return result.rows;
};

const getIssueImageById = async (imageId) => {
  const query = `
    SELECT
      id,
      issue_id,
      image_url,
      uploaded_at
    FROM issue_images
    WHERE id = $1;
  `;

  const result = await pool.query(query, [imageId]);

  return result.rows[0];
};

const deleteIssueImage = async (imageId) => {
  const query = `
    DELETE FROM issue_images
    WHERE id = $1
    RETURNING *;
  `;

  const result = await pool.query(query, [imageId]);

  return result.rows[0];
};

module.exports = {
  createIssueImage,
  getIssueImages,
  getIssueImageById,
  deleteIssueImage,
};