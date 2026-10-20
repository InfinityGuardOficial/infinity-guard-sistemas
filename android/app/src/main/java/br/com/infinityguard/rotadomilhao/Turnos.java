package br.com.infinityguard.rotadomilhao;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import java.util.Calendar;

/** Horários padrão dos turnos (os mesmos do app). Cada turno toca todo dia; o receptor confere o dia da semana. */
final class Turnos {
    static final String[] ID = {"manha", "almoco", "noite", "sabado", "domingo"};
    static final String[] NOME = {"Antes do trabalho", "Almoço", "Noite", "Bloco de sábado", "Revisão de domingo"};
    static final String[] TEXTO = {
        "Zerar o WhatsApp, ler o radar da equipe e 1 story.",
        "Missão de conteúdo do dia.",
        "Módulo da semana e números do dia no Placar.",
        "Pacote da semana no Planejador e prova do módulo.",
        "15 minutos de revisão: execução, meta e 1 decisão."
    };
    static final int[][] HORA = {{6, 0}, {12, 10}, {20, 0}, {9, 0}, {19, 0}};

    static boolean valeHoje(int i, int diaDaSemana) {
        if (i <= 2) return diaDaSemana >= Calendar.MONDAY && diaDaSemana <= Calendar.FRIDAY;
        if (i == 3) return diaDaSemana == Calendar.SATURDAY;
        return diaDaSemana == Calendar.SUNDAY;
    }

    static void agendarTodos(Context ctx) {
        AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
        for (int i = 0; i < ID.length; i++) {
            Intent it = new Intent(ctx, TurnoReceiver.class).putExtra("turno", i);
            PendingIntent pi = PendingIntent.getBroadcast(ctx, i, it, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
            Calendar c = Calendar.getInstance();
            c.set(Calendar.HOUR_OF_DAY, HORA[i][0]);
            c.set(Calendar.MINUTE, HORA[i][1]);
            c.set(Calendar.SECOND, 0);
            c.add(Calendar.MINUTE, -5);
            if (c.getTimeInMillis() <= System.currentTimeMillis()) c.add(Calendar.DAY_OF_YEAR, 1);
            am.setInexactRepeating(AlarmManager.RTC_WAKEUP, c.getTimeInMillis(), AlarmManager.INTERVAL_DAY, pi);
        }
    }

    private Turnos() {}
}
