package com.wildux.moras;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.ContentValues;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.annotation.NonNull;
import android.util.Base64;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Toast;

import java.io.BufferedOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.SocketTimeoutException;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;
import java.util.zip.GZIPOutputStream;

/**
 * Created by joan on 14/11/16
 */
public class MainActivity extends Activity implements View.OnClickListener {

    private Settings settings;

    //keep track of intents
    final int CAMERA_CAPTURE = 1;
    final int PIC_CROP = 2;
    public static final int RESULT_GALLERY = 3;

    //captured picture uri
    private Uri picUri = Uri.EMPTY;
    private Uri destination = Uri.EMPTY;

    // Save the activity state when it's going to stop.
    @Override
    public void onSaveInstanceState(Bundle savedInstanceState) {
        savedInstanceState.putString("picUri", picUri.toString());
        super.onSaveInstanceState(savedInstanceState);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (savedInstanceState != null) {
            picUri = Uri.parse(savedInstanceState.getString("picUri"));
        }

        //retrieve a reference to the UI button
        Button captureBtn = (Button)findViewById(R.id.capture_btn);
        Button browseBtn = (Button)findViewById(R.id.browse_btn);
        Button optionsBtn = (Button)findViewById(R.id.options_btn);
        //handle button clicks
        captureBtn.setOnClickListener(this);
        browseBtn.setOnClickListener(this);
        optionsBtn.setOnClickListener(this);
        settings = new Settings(this);
    }

    public void onClick(View v) {
        if (v.getId() == R.id.capture_btn) {
            try {

                //camera stuff
                Intent captureIntent = new Intent(android.provider.MediaStore.ACTION_IMAGE_CAPTURE);
                /*String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());

                //folder stuff
                File imagesFolder = new File(Environment.getExternalStorageDirectory(), "MyImages");
                imagesFolder.mkdirs();

                File image = new File(imagesFolder, "QR_" + timeStamp + ".png");
                picUri = Uri.fromFile(image);

                captureIntent.putExtra(MediaStore.EXTRA_OUTPUT, picUri);
*/

                Toast.makeText(this, "URI: " + picUri, Toast.LENGTH_LONG).show();

                //updateDestination();

                //we will handle the returned data in onActivityResult
                startActivityForResult(captureIntent, CAMERA_CAPTURE);

                //start image scanne to add photo to gallery
                //addProductPhotoToGallery(picUri);
            }
            catch(ActivityNotFoundException anfe){
                //display an error message
                String errorMessage = "Whoops - your device doesn't support capturing images!";
                Toast toast = Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT);
                toast.show();
            }
        }

        else if (v.getId() == R.id.browse_btn) {
            try {
                //use standard intent to capture an image
                Intent galleryIntent = new Intent(
                        Intent.ACTION_PICK,
                        android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI);

                //we will handle the returned data in onActivityResult
                startActivityForResult(galleryIntent, RESULT_GALLERY);
            }
            catch(ActivityNotFoundException anfe){
                //display an error message
                String errorMessage = "Whoops - your device doesn't support gallery!";
                Toast toast = Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT);
                toast.show();
            }
        }
        else if (v.getId() == R.id.options_btn) {
            try {
                //use standard intent to capture an image
                Intent it = new Intent(this,SettingsActivity.class);
                startActivity(it);
            }
            catch(ActivityNotFoundException anfe){
                //display an error message
                String errorMessage = "Whoops - your device doesn't support gallery!";
                Toast toast = Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT);
                toast.show();
            }
        }
    }

    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (resultCode == RESULT_OK) {
            //user is returning from capturing an image using the camera
            if(requestCode == CAMERA_CAPTURE){
                //picUri = Uri.parse("content://media/external/images/media/26681");
                //get the Uri for the captured image
                if (data == null) {
                    Toast.makeText(this, "Null data", Toast.LENGTH_LONG).show();
                    //performCrop();
                } else {
                    //Toast.makeText(this, "OK", Toast.LENGTH_LONG).show();
                    //picUri = data.getData();
                    Toast.makeText(this, "OK, " + data.getData(), Toast.LENGTH_LONG).show();
                    //performCrop();
                }
            }
            else if(requestCode == RESULT_GALLERY) {
                //get the Uri for the captured image
                if (data == null) {
                    Toast.makeText(this, "Null data", Toast.LENGTH_LONG).show();

                } else {
                    picUri = data.getData();
                    Toast.makeText(this, "URI: " + picUri, Toast.LENGTH_LONG).show();
                    performCrop();
                }
            }

            //user is returning from cropping the image
            else if(requestCode == PIC_CROP){
                //get the returned data
                Bundle extras = data.getExtras();

                Bitmap thePic = extras.getParcelable("data");
                String encodedImage = encodeToBase64(thePic,Bitmap.CompressFormat.PNG, 100);

                //callServer(encodedImage);
                //Log.w("PICTURE:", encodedImage);

                //LOG
                /*final int chunkSize = 2048;
                for (int i = 0; i < encodedImage.length(); i += chunkSize) {
                    Log.w("PICTURE:", encodedImage.substring(i, Math.min(encodedImage.length(), i + chunkSize)));
                }*/

                ImageView picView = (ImageView)findViewById(R.id.picture);
                picView.setImageBitmap(thePic);
            }
        }
    }

    /*private String encodeOK(Bitmap image) {
        String encodedImage = "";
        ByteArrayOutputStream stream = new ByteArrayOutputStream();
        try {
            GZIPOutputStream gzipOstream = null;
            try {
                gzipOstream = new GZIPOutputStream(stream);
                image.compress(Bitmap.CompressFormat.JPEG, 100, gzipOstream);
                gzipOstream.flush();
            } finally {
                gzipOstream.close();
                stream.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
            stream = null;
        }
        if(stream != null) {
            byte[] byteArry=stream.toByteArray();
            encodedImage = Base64.encodeToString(byteArry, Base64.NO_WRAP);
        }
        return encodedImage;
    }*/

    public static String encodeToBase64(Bitmap image, Bitmap.CompressFormat compressFormat, int quality)
    {
        ByteArrayOutputStream byteArrayOS = new ByteArrayOutputStream();
        image.compress(compressFormat, quality, byteArrayOS);
        return Base64.encodeToString(byteArrayOS.toByteArray(), Base64.URL_SAFE);
    }

    public static Bitmap decodeBase64(String input)
    {
        byte[] decodedBytes = Base64.decode(input, 0);
        return BitmapFactory.decodeByteArray(decodedBytes, 0, decodedBytes.length);
    }

    private void performCrop(){
        try {
            Intent cropIntent = new Intent("com.android.camera.action.CROP"); //Build-in crop
            cropIntent.setDataAndType(picUri, "image/*"); //Uri + type
            cropIntent.putExtra("crop", "true");
            cropIntent.putExtra("return-data", true);
            startActivityForResult(cropIntent, PIC_CROP);
        }
        catch(ActivityNotFoundException anfe){
            String errorMessage = "Your device doesn't support the crop action!";
            Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show();
        }
    }

    private void callServer(String image) {
        int ps = settings.getPoint_selector();
        int fe = settings.getFeature_extractor();
        boolean rs = settings.isRansac();
        String rob = settings.getRobot_add();
        String uri = Uri.parse("http://wildux.pythonanywhere.com/MORAS/default/image_dimensions")
                .buildUpon()
                .appendQueryParameter("ps", "HARRIS")
                .build().toString();
        //HttpGet httpget = new HttpGet(uri);
        HttpURLConnection client = null;
        try {
            URL url = new URL("http://wildux.pythonanywhere.com/MORAS/default/image_dimensions");
            client = (HttpURLConnection) url.openConnection();
            client.setRequestMethod("POST");//setRequestMode("POST");
            client.setRequestProperty("ps","HARRIS");
            client.setDoOutput(true);

            OutputStream outputPost = new BufferedOutputStream(client.getOutputStream());
            writeStream(outputPost);
            outputPost.flush();
            outputPost.close();
        }
        catch(MalformedURLException error) {
            //Handles an incorrectly entered URL
        }
        catch(SocketTimeoutException error) {
        //Handles URL access timeout.
        }
        catch (IOException error) {
        //Handles input and output errors
        }
        finally {
            if(client != null) // Make sure the connection is not null.
                client.disconnect();
        }

        // call(image, ps, fe, rs, rob)
    }

    /*

    // Recover the saved state when the activity is recreated.
    @Override
    protected void onRestoreInstanceState(@NonNull Bundle savedInstanceState) {
        super.onRestoreInstanceState(savedInstanceState);

        picUri = savedInstanceState.getParcelable("picUri");

    }*/
    private void updateDestination() {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyyD_HHmmss");
        String timeString = sdf.format(Calendar.getInstance().getTime());
        Toast toast = Toast.makeText(this, timeString, Toast.LENGTH_SHORT);
        //toast.show();

        Uri urii = Uri.parse("content://media/external/images/media/26681");
        String path = urii.getPath();
        toast = Toast.makeText(this, path, Toast.LENGTH_SHORT);
        toast.show();
        //File image = new File(imagesFolder, timeString + ".png");
        //Uri uriSavedImage = Uri.fromFile(image);
    }

    private File getProductPhotoDirectory() {
        //get directory where file should be stored
        return new File(Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_PICTURES),
                "myPhotoDir");
    }

    private Uri getPhotoFileUri(final String photoStorePath) {

        //timestamp used in file name
        final String timestamp = new SimpleDateFormat("yyyyMMdd_HHmmss",
                Locale.US).format(new Date());

        // file uri with timestamp
        final Uri fileUri = Uri.fromFile(new java.io.File(photoStorePath
                + java.io.File.separator + "IMG_" + timestamp + ".jpg"));

        return fileUri;
    }

    private void addProductPhotoToGallery(Uri photoUri) {
        //create media scanner intetnt
        Intent mediaScanIntent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);

        //set uri to scan
        mediaScanIntent.setData(photoUri);
        //start media scanner to discover new photo and display it in gallery
        this.sendBroadcast(mediaScanIntent);
    }


}
