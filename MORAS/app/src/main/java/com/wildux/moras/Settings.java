package com.wildux.moras;


import android.content.Context;
import android.content.SharedPreferences;

/**
 * Created by joan on 15/11/16
 */
public class Settings {

    private SharedPreferences sp;

    private int point_selector;
    private int feature_extractor;
    private boolean ransac;
    private String robot_add;

    public static final int HARRIS = 0;
    public static final int SHI_TOMASI = 1 ;
    public static final int DOG = 2;

    public static final int SIFT = 0;
    public static final int SURF = 1;
    public static final int LATCH = 2;

    public Settings(Context context) {
        sp = context.getSharedPreferences("achievements", Context.MODE_PRIVATE);

        point_selector = sp.getInt("point_selector", SHI_TOMASI);
        feature_extractor = sp.getInt("feature_extractor", SIFT);
        ransac = sp.getBoolean("ransac", true);
        robot_add = sp.getString("robot_add", "0.0.0.0");
    }

    public int getPoint_selector() {
        return point_selector;
    }

    public void setPoint_selector(int point_selector) {
        this.sp.edit().putInt("point_selector", point_selector).apply();
    }

    public int getFeature_extractor() {
        return feature_extractor;
    }

    public void setFeature_extractor(int feature_extractor) {
        this.sp.edit().putInt("feature_extractor", feature_extractor).apply();
    }

    public boolean isRansac() {
        return ransac;
    }

    public void setRansac(boolean ransac) {
        this.sp.edit().putBoolean("ransac", ransac).apply();
    }

    public String getRobot_add() {
        return robot_add;
    }

    public void setRobot_add(String robot_add) {
        this.sp.edit().putString("robot_add", robot_add).apply();
    }
}
