package br.com.infinityguard.rotadomilhao;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.webkit.CookieManager;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/** Abre o Rota do Milhão (página privada no claude.ai) com o login do dono e agenda os avisos dos turnos. */
public class MainActivity extends Activity {
    static final String URL_APP = "https://claude.ai/artifact/V2LctZDwDPV4Ly9S8P8KJx";
    private static final int PEDIDO_ARQUIVO = 10;
    private WebView web;
    private ValueCallback<Uri[]> callbackArquivo;

    @Override
    protected void onCreate(Bundle estado) {
        super.onCreate(estado);
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 1);
        }
        Turnos.agendarTodos(this);

        web = new WebView(this);
        setContentView(web);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setUserAgentString(s.getUserAgentString().replace("; wv", ""));
        CookieManager.getInstance().setAcceptCookie(true);
        CookieManager.getInstance().setAcceptThirdPartyCookies(web, true);

        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest req) {
                String host = req.getUrl().getHost() == null ? "" : req.getUrl().getHost();
                if (host.endsWith("claude.ai") || host.endsWith("anthropic.com") || host.endsWith("claudeusercontent.com")) return false;
                startActivity(new Intent(Intent.ACTION_VIEW, req.getUrl()));
                return true;
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> cb, FileChooserParams p) {
                if (callbackArquivo != null) callbackArquivo.onReceiveValue(null);
                callbackArquivo = cb;
                try {
                    startActivityForResult(p.createIntent(), PEDIDO_ARQUIVO);
                } catch (Exception e) {
                    callbackArquivo = null;
                    return false;
                }
                return true;
            }
        });
        if (estado != null) web.restoreState(estado); else web.loadUrl(URL_APP);
    }

    @Override
    protected void onActivityResult(int pedido, int resultado, Intent dados) {
        if (pedido == PEDIDO_ARQUIVO && callbackArquivo != null) {
            callbackArquivo.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(resultado, dados));
            callbackArquivo = null;
        }
        super.onActivityResult(pedido, resultado, dados);
    }

    @Override
    protected void onSaveInstanceState(Bundle out) { super.onSaveInstanceState(out); web.saveState(out); }

    @Override
    public void onBackPressed() { if (web.canGoBack()) web.goBack(); else moveTaskToBack(true); }

    @Override
    protected void onPause() { super.onPause(); CookieManager.getInstance().flush(); }
}
