import React, { useEffect, useState } from "react";

// Lets the user pick an optional profile picture during signup.
// The file is NOT uploaded here: it is sent together with the signup form
// (see signUp in store/session.js), because uploads require a logged-in user.
function ProPicImageUpload({ setImage }) {
  const [previewUrl, setPreviewUrl] = useState("");

  useEffect(() => {
    // Free the temporary preview URL when it changes or the form unmounts.
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const updateImage = (e) => {
    const file = e.target.files[0] || null;
    setImage(file);
    setPreviewUrl(file ? URL.createObjectURL(file) : "");
  };

  return (
    <div className="field">
      <label htmlFor="signup-photo">Profile photo (optional)</label>
      <div className="signup-pic">
        {previewUrl && <img src={previewUrl} alt="Preview of your profile photo" className="avatar" />}
        <input
          id="signup-photo"
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={updateImage}
        />
      </div>
    </div>
  );
}

export default ProPicImageUpload;
