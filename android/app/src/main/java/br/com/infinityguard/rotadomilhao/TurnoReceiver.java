package br.com.infinityguard.rotadomilhao;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import java.util.Calendar;

/** Mostra o aviso do turno (cerca de 5 minutos antes do horário). */
public class TurnoReceiver extends BroadcastReceiver {
    private static final String CANAL = "turnos";

    @Override
    public void onReceive(Context ctx, Intent intent) {
        int i = intent.getIntExtra("turno", -1);
        if (i < 0 || i >= Turnos.ID.length) return;
        if (!Turnos.valeHoje(i, Calendar.getInstance().get(Calendar.DAY_OF_WEEK))) return;

        NotificationManager nm = (NotificationManager) ctx.getSystemService(Context.NOTIFICATION_SERVICE);
        if (Build.VERSION.SDK_INT >= 26 && nm.getNotificationChannel(CANAL) == null) {
            nm.createNotificationChannel(new NotificationChannel(CANAL, "Turnos do Rota do Milhão", NotificationManager.IMPORTANCE_HIGH));
        }
        PendingIntent abrir = PendingIntent.getActivity(ctx, 100 + i, new Intent(ctx, MainActivity.class), PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        Notification.Builder b = Build.VERSION.SDK_INT >= 26 ? new Notification.Builder(ctx, CANAL) : new Notification.Builder(ctx);
        b.setSmallIcon(android.R.drawable.ic_lock_idle_alarm)
         .setContentTitle(Turnos.NOME[i] + " começa já")
         .setContentText(Turnos.TEXTO[i])
         .setStyle(new Notification.BigTextStyle().bigText(Turnos.TEXTO[i] + " Abra o app e coloque a prova."))
         .setContentIntent(abrir)
         .setAutoCancel(true);
        try { nm.notify(200 + i, b.build()); } catch (SecurityException e) { /* sem permissão de notificação */ }
    }
}
