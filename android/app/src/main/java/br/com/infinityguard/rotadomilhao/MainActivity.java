package br.com.infinityguard.rotadomilhao;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import androidx.browser.customtabs.CustomTabColorSchemeParams;
import androidx.browser.customtabs.CustomTabsIntent;

/**
 * Abre o Rota do Milhão (página privada no claude.ai) numa aba do Chrome integrada ao app.
 * O login fica no Chrome, então funciona com e-mail, Google ou Apple. Também agenda os avisos dos turnos.
 */
public class MainActivity extends Activity {
    static final String URL_APP = "https://claude.ai/artifact/V2LctZDwDPV4Ly9S8P8KJx";

    @Override
    protected void onCreate(Bundle estado) {
        super.onCreate(estado);
        Turnos.agendarTodos(this);
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 1);
        } else {
            abrir();
        }
    }

    @Override
    public void onRequestPermissionsResult(int pedido, String[] permissoes, int[] resultados) {
        abrir();
    }

    private void abrir() {
        CustomTabsIntent aba = new CustomTabsIntent.Builder()
            .setDefaultColorSchemeParams(new CustomTabColorSchemeParams.Builder().setToolbarColor(0xFF001121).build())
            .setShowTitle(true)
            .build();
        try {
            aba.launchUrl(this, Uri.parse(URL_APP));
        } catch (Exception e) {
            startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(URL_APP)));
        }
        finish();
    }
}
