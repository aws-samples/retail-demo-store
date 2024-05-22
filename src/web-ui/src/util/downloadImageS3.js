import { Storage } from 'aws-amplify';

export const downloadImageS3 = async (key) => {
    try {
      const signedUrl = await Storage.get(key, {
        level: 'private',
      });
      return signedUrl
    } catch (error) {
      console.error('Error fetching the image:', error);
    }
};