package com.wildux.moras;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;

import java.io.File;
import java.util.HashMap;
import java.util.Map;


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
    private ImageView picView;

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
        picView = (ImageView) findViewById(R.id.picture);
        //handle button clicks
        captureBtn.setOnClickListener(this);
        browseBtn.setOnClickListener(this);
        optionsBtn.setOnClickListener(this);
    }

    @Override
    public void onResume() {
        super.onResume();
        settings = new Settings(getApplicationContext());
    }

    public void onClick(View v) {
        if (v.getId() == R.id.capture_btn) try {
            Intent captureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
            startActivityForResult(captureIntent, CAMERA_CAPTURE);
        } catch (ActivityNotFoundException anfe) {
            String errorMessage = "Your device doesn't support capturing images!";
            Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show();
        }

        else if (v.getId() == R.id.browse_btn) try {
            Intent galleryIntent = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
            startActivityForResult(galleryIntent, RESULT_GALLERY);
        } catch (ActivityNotFoundException anfe) {
            String errorMessage = "Your device doesn't support gallery access!";
            Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show();
        }

        else if (v.getId() == R.id.options_btn) try {
            Intent it = new Intent(this, SettingsActivity.class);
            startActivity(it);
        } catch (ActivityNotFoundException anfe) {
            String errorMessage = "Unknown error";
            Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show();
        }
    }

    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (resultCode == RESULT_OK)
            switch (requestCode) {
                case CAMERA_CAPTURE:
                    String path = getLastImage();
                    if (data == null || path == null) Toast.makeText(this, "Null data", Toast.LENGTH_LONG).show();
                    else {
                        picUri = Uri.fromFile(new File(path));
                        performCrop();
                    }
                    break;

                case RESULT_GALLERY:
                    if (data == null) {
                        Toast.makeText(this, "Null data", Toast.LENGTH_LONG).show();
                    } else {
                        picUri = data.getData();
                        performCrop();
                    }
                    break;

                case PIC_CROP:
                    Bundle extras = data.getExtras();

                    Bitmap thePic = extras.getParcelable("data");
                    //String encodedImage = encodeToBase64(thePic, Bitmap.CompressFormat.PNG, 100);

                    /*final int chunkSize = 2048;
                    for (int i = 0; i < encodedImage.length(); i += chunkSize) {
                        Log.w("PICTURE:", encodedImage.substring(i, Math.min(encodedImage.length(), i + chunkSize)));
                    }*/

                    //sendRequest(encodedImage);

                    picView.setImageBitmap(thePic);
                    break;
            }
    }

    /*
    public static String encodeToBase64(Bitmap image, Bitmap.CompressFormat compressFormat, int quality)
    {
        ByteArrayOutputStream byteArrayOS = new ByteArrayOutputStream();
        image.compress(compressFormat, quality, byteArrayOS);
        return Base64.encodeToString(byteArrayOS.toByteArray(), Base64.URL_SAFE);
    }

    public static Bitmap decodeBase64(String input)
    {
        byte[] decodedBytes = Base64.decode(input, Base64.URL_SAFE);
        return BitmapFactory.decodeByteArray(decodedBytes, 0, decodedBytes.length);
    }*/

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

    private void sendRequest(final String encodedImage) {
        final TextView mTextView = (TextView) findViewById(R.id.text);
        // Instantiate the RequestQueue.
        RequestQueue queue = Volley.newRequestQueue(this);
        String url = "http://wildux.pythonanywhere.com/MORAS/default/image_dimensions";
        mTextView.setText("Waiting response...");

        // Request a string response from the provided URL.
        StringRequest stringRequest = new StringRequest(Request.Method.POST, url,
            new Response.Listener<String>() {
                @Override
                public void onResponse(String response) {
                    // Display the first 500 characters of the response string.
                    mTextView.setText(response);
                }
            }, new Response.ErrorListener() {
                @Override
                public void onErrorResponse(VolleyError error) {
                    mTextView.setText("That didn't work!");
                }
            }
        )
        {
            @Override
            protected Map<String, String> getParams() {
                int ps = settings.getPoint_selector();
                int fe = settings.getFeature_extractor();
                boolean rs = settings.isRansac();
                String rob = settings.getRobot_add();

                Map<String, String> params = new HashMap<>();
                //params.put("img", encodedImage);
                params.put("ps", Integer.toString(ps));
                params.put("fe", Integer.toString(fe));
                params.put("ransac",Boolean.toString(rs));
                params.put("robot",rob);

                //Log.w("PARAMS: ",params.toString());

                return params;
            }
        };
        // Add the request to the RequestQueue.
        queue.add(stringRequest);
    }

    /*
    private void setPic() {
        String mCurrentPhotoPath = getLastImageId();
        // Get the dimensions of the View
        int targetW = 200;
        int targetH = 200;

        // Get the dimensions of the bitmap
        BitmapFactory.Options bmOptions = new BitmapFactory.Options();
        bmOptions.inJustDecodeBounds = true;
        BitmapFactory.decodeFile(mCurrentPhotoPath, bmOptions);
        int photoW = bmOptions.outWidth;
        int photoH = bmOptions.outHeight;

        // Determine how much to scale down the image
        int scaleFactor = Math.min(photoW/targetW, photoH/targetH);

        // Decode the image file into a Bitmap sized to fill the View
        bmOptions.inJustDecodeBounds = false;
        //bmOptions.inSampleSize = scaleFactor << 1;
        bmOptions.inPurgeable = true;

        Bitmap bitmap = BitmapFactory.decodeFile(mCurrentPhotoPath, bmOptions);

        //Matrix mtx = new Matrix();
        //mtx.postRotate(90);
        // Rotating Bitmap
        //Bitmap rotatedBMP = Bitmap.createBitmap(bitmap, 0, 0, bitmap.getWidth(), bitmap.getHeight(), mtx, true);

        //if (rotatedBMP != bitmap) bitmap.recycle();


        picView.setImageBitmap(bitmap);
    }
    */

    private String getLastImage(){
        final String[] imageColumns = { MediaStore.Images.Media._ID, MediaStore.Images.Media.DATA };
        final String imageOrderBy = MediaStore.Images.Media._ID+" DESC";
        Cursor cursor = getContentResolver().query(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, imageColumns, null, null, imageOrderBy);
        if(cursor.moveToFirst()){
            //int id = imageCursor.getInt(imageCursor.getColumnIndex(MediaStore.Images.Media._ID));
            String fullPath = cursor.getString(cursor.getColumnIndex(MediaStore.Images.Media.DATA));
            //Log.d("ID: ", "getLastImageId::id " + id);
            Log.d("ID: ", "getLastImageId::path " + fullPath);
            cursor.close();
            return fullPath;
        }else return null;
    }



}
