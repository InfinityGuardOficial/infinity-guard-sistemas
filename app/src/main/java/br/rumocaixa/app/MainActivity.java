package br.rumocaixa.app;

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
 * Abre o Rumo à Caixa 2027 (página privada no claude.ai) numa aba do Chrome integrada ao app,
 * igual ao Rota do Milhão. O progresso fica na conta Claude, então app e link mostram o mesmo.
 * Também agenda os avisos dos turnos de estudo.
 */
public class MainActivity extends Activity {
    static final String URL_APP = "https://claude.ai/artifact/1feHirXXhyjXrb3SosyDd1";

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
            .setDefaultColorSchemeParams(new CustomTabColorSchemeParams.Builder().setToolbarColor(0xFF0B3D91).build())
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
