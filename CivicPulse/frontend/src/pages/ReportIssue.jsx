import { useState } from "react";
import { apiRequest, uploadImages } from "../services/api";

function ReportIssue() {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    category: "",
    priority: "",
    latitude: "",
    longitude: "",
    address: "",
  });

  const [images, setImages] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
  e.preventDefault();

  setMessage("");
  setError("");

  try {
    // Step 1: Create the issue
    const data = await apiRequest("/api/issues", {
      method: "POST",
      body: JSON.stringify({
        ...formData,
        latitude: Number(formData.latitude),
        longitude: Number(formData.longitude),
      }),
    });

    console.log("Issue reported successfully:", data);

    // Get the newly created issue ID
    const issueId = data.issue.id;

    // Step 2: Upload images if any were selected
    if (images.length > 0) {
      const imageFormData = new FormData();

      images.forEach((image) => {
        imageFormData.append("images", image);
      });

      const imageData = await uploadImages(
        `/api/issues/${issueId}/images`,
        imageFormData
      );

      console.log("Images uploaded successfully:", imageData);
    }

    // Step 3: Show final success message
    setMessage("Issue reported successfully!");

    // Reset form
    setFormData({
      title: "",
      description: "",
      category: "",
      priority: "",
      latitude: "",
      longitude: "",
      address: "",
    });

    setImages([]);
  } catch (error) {
    console.error("Failed to report issue:", error.message);
    setError(error.message);
  }
};

  return (
    <div>
      <h1>Report a Civic Issue</h1>

      {message && <p>{message}</p>}
      {error && <p>{error}</p>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="title">Title</label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="Enter issue title"
            required
          />
        </div>

        <div>
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Describe the issue"
            required
          />
        </div>

        <div>
          <label htmlFor="category">Category</label>
          <select
            id="category"
            name="category"
            value={formData.category}
            onChange={handleChange}
            required
          >
            <option value="">Select category</option>
            <option value="pothole">Pothole</option>
            <option value="road_damage">Road Damage</option>
            <option value="garbage">Garbage</option>
            <option value="streetlight">Streetlight</option>
            <option value="water_leakage">Water Leakage</option>
            <option value="damaged_infrastructure">
              Damaged Infrastructure
            </option>
          </select>
        </div>

        <div>
          <label htmlFor="priority">Priority</label>
          <select
            id="priority"
            name="priority"
            value={formData.priority}
            onChange={handleChange}
            required
          >
            <option value="">Select priority</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>

        <div>
          <label htmlFor="latitude">Latitude</label>
          <input
            type="number"
            step="any"
            id="latitude"
            name="latitude"
            value={formData.latitude}
            onChange={handleChange}
            placeholder="e.g. 30.7333"
            required
          />
        </div>

        <div>
          <label htmlFor="longitude">Longitude</label>
          <input
            type="number"
            step="any"
            id="longitude"
            name="longitude"
            value={formData.longitude}
            onChange={handleChange}
            placeholder="e.g. 76.7794"
            required
          />
        </div>

        <div>
          <label htmlFor="address">Address</label>
          <input
            type="text"
            id="address"
            name="address"
            value={formData.address}
            onChange={handleChange}
            placeholder="Enter address"
          />
        </div>

        <div>
          <label htmlFor="images">Issue Images</label>
          <input
            type="file"
            id="images"
            name="images"
            accept="image/jpeg,image/png,image/webp"
            multiple
            onChange={(e) => setImages(Array.from(e.target.files))}
          />
        </div>

        <button type="submit">Report Issue</button>
      </form>
    </div>
  );
}

export default ReportIssue;