import React, { useState } from "react";
import "./ImageUploadComponent.css";
import apiFetch from "../../../utils/apiFetch";
//!pass in a setValue from postForm to get the image url.
// Uploads the picked file; the server shrinks it and answers with the public
// URLs and size, which are handed up through onUploaded.
const ImageUploadComponent = ({ onUploaded }) => {
  const [image, setImage] = useState(null);
  const [imageLoading, setImageLoading] = useState(false);
  const [uploadedImg, setUploadImg] = useState(false);
  const [prevImgUrl, setPrevImgUrl] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();

    // aws uploads can be a bit slow—displaying
    // some sort of loading message is a good idea

    setImageLoading(true);

    formData.append("image", image);
    const res = await apiFetch("/api/img/upload", {
      method: "POST",
      body: formData,
    });
    if (res.ok) {
      const uploaded = await res.json();
      setImageLoading(false);
      onUploaded(uploaded);
      setUploadImg(true);
      setPrevImgUrl(uploaded.thumbUrl || uploaded.url);
    } else {
      setImageLoading(false);
      // a real app would probably use more advanced
      // error handling
    }
  };

  const updateImage = (e) => {
    const file = e.target.files[0];
    setImage(file);
  };

  return (
    <>
      <form onSubmit={handleSubmit}>
        <div className="upload-photo-container">
          <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={updateImage} />
          <button type="submit" className="upload-img-btn">Upload</button>
        </div>
        {imageLoading && <p>Loading...</p>}
      </form>
      {uploadedImg && (
        <img src={prevImgUrl} alt="your image" className="prev_img" />
      )}
    </>
  );
};

export default ImageUploadComponent;
