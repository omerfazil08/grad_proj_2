fs = 12000;                         % sampling frequency (Hz)
N = length(X097_DE_time);
t = (0:N-1)/fs;                     % time vector

figure
plot(t, X097_DE_time)
grid on
xlabel('Time (s)')
ylabel('Amplitude')
title('Drive End Vibration Signal (Time Domain)')
