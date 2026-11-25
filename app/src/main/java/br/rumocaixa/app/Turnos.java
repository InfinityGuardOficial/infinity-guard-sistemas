package br.rumocaixa.app;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import java.util.Calendar;

/** Horários padrão dos turnos (os mesmos do app). Cada turno toca todo dia; o receptor confere o dia da semana. */
final class Turnos {
    static final String[] NOME = {"Almoço: flashcards", "Almoço: questões", "Noite: módulo", "Leitura", "Bloco de sábado", "Redação de domingo"};
    static final int[][] HORA = {{12, 20}, {12, 35}, {19, 0}, {21, 15}, {13, 0}, {16, 0}};

    static boolean valeHoje(int i, int dia) {
        if (i <= 2) return dia >= Calendar.MONDAY && dia <= Calendar.FRIDAY;
        if (i == 3) return true;
        if (i == 4) return dia == Calendar.SATURDAY;
        return dia == Calendar.SUNDAY;
    }

    static String texto(int i, int dia) {
        switch (i) {
            case 0: return "15 minutos de flashcards do dia.";
            case 1: return (dia == Calendar.MONDAY || dia == Calendar.WEDNESDAY)
                ? "Questões da matéria do módulo da semana." : "Bloco de questões misturadas.";
            case 2:
                switch (dia) {
                    case Calendar.MONDAY: return "Aula do módulo e apostila.";
                    case Calendar.TUESDAY: return "Vídeo do módulo.";
                    case Calendar.WEDNESDAY: return "Leitura oficial e tarefa do módulo.";
                    case Calendar.THURSDAY: return "Quiz (70% para passar) e resumo do módulo.";
                    default: return "Faculdade e inglês.";
                }
            case 3: return "20 minutos do livro do mês. Anote as páginas no app.";
            case 4: return "Feche o que faltou do módulo, questões e simulado.";
            default: return "Redação com cronômetro e revisão da semana.";
        }
    }

    static void agendarTodos(Context ctx) {
        AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
        for (int i = 0; i < NOME.length; i++) {
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
