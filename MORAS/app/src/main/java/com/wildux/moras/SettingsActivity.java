package com.wildux.moras;

import android.app.Activity;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;
import android.widget.ToggleButton;

public class SettingsActivity extends Activity implements AdapterView.OnItemSelectedListener {

    private Settings settings;
    private Spinner sp_points, sp_features;
    private ToggleButton tb_ransac;
    private EditText txt_robot;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);

        settings = new Settings(this);

        sp_points = (Spinner) findViewById(R.id.sp_points);
        ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(this,
        R.array.point_selector_list, android.R.layout.simple_spinner_item);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        sp_points.setAdapter(adapter);
        sp_points.setOnItemSelectedListener(this);

        sp_features = (Spinner) findViewById(R.id.sp_features);
        ArrayAdapter<CharSequence> adapter2 = ArrayAdapter.createFromResource(this,
        R.array.feature_extractor_list, android.R.layout.simple_spinner_item);
        adapter2.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        sp_features.setAdapter(adapter2);
        sp_features.setOnItemSelectedListener(this);

        tb_ransac = (ToggleButton) findViewById(R.id.tb_ransac);
        txt_robot = (EditText) findViewById(R.id.et_robot);

        txt_robot.addTextChangedListener(new TextWatcher() {

            @Override
            public void afterTextChanged(Editable s) {
                settings.setRobot_add(txt_robot.getText().toString());
            }

            @Override
            public void beforeTextChanged(CharSequence s, int start,
                                          int count, int after) {
            }

            @Override
            public void onTextChanged(CharSequence s, int start,
                                      int before, int count) {
                //if(s.length() != 0);
            }
        });

        tb_ransac.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                settings.setRansac(isChecked);
            }
        });

        initOptions();
    }

    public void onItemSelected(AdapterView<?> parent, View view, int pos, long id) {
        // An item was selected. You can retrieve the selected item using
        switch (parent.getId())
        {
            case R.id.sp_points:
                settings.setPoint_selector((int)id);
                break;

            case R.id.sp_features:
                settings.setFeature_extractor((int)id);
                break;
        }
        //String it = parent.getItemAtPosition(pos).toString();
        //String it = Long.toString(id);
        //Toast.makeText(SettingsActivity.this, it, Toast.LENGTH_SHORT).show();
    }

    public void onNothingSelected(AdapterView<?> parent) {
        // Another interface callback
    }

    private void initOptions(){
        int ps = settings.getPoint_selector();
        int fe = settings.getFeature_extractor();
        boolean rs = settings.isRansac();
        String robot = settings.getRobot_add();

        sp_points.setSelection(ps);
        sp_features.setSelection(fe);
        tb_ransac.setChecked(rs);
        txt_robot.setText(robot);
    }
}