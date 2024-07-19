import { getUrl } from 'aws-amplify/storage';

export const downloadImageS3 = async (key) => {
    try {
      const signedUrl = await getUrl({
        path: ({identityId}) => `private/${identityId}/${key}`
      });
      return signedUrl.url
    } catch (error) {
      console.error('Error fetching the image:', error);
    }
};