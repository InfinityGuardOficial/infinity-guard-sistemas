package br.com.infinityguard.rotadomilhao;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** Reagenda os avisos depois que o celular reinicia. */
public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context ctx, Intent intent) {
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) Turnos.agendarTodos(ctx);
    }
}
