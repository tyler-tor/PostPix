import React, { useEffect, useState } from "react";
import './LoginPage.css'

// Lets the user pick an optional profile picture during signup.
// The file is NOT uploaded here: it is sent together with the signup form
// (see signUp in store/session.js), because uploads require a logged-in user.
function ProPicImageUpload({ setImage }) {
    const [previewUrl, setPreviewUrl] = useState('');

    useEffect(() => {
        // Free the temporary preview URL when it changes or the form unmounts.
        return () => { if (previewUrl) URL.revokeObjectURL(previewUrl); };
    }, [previewUrl]);

    const updateImage = (e) => {
        const file = e.target.files[0] || null;
        setImage(file);
        setPreviewUrl(file ? URL.createObjectURL(file) : '');
    };

    return (
        <div className="signup-propic-wrapper">
            <div className="supp-input-btn-wrapper">
                <input type='file' accept='image/jpeg,image/png,image/webp,image/gif' onChange={updateImage} />
            </div>
            {previewUrl && (
                <img src={previewUrl} alt='Profile preview' className='supp-prev-img' />
            )}
        </div>
    )
}

export default ProPicImageUpload
