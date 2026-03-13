clc; clear;

files = {'97.mat', '105.mat', '118.mat', '130.mat'};
fs = 12000;   % sampling frequency (Hz)

figure

for k = 1:length(files)
    % Load file
    S = load(files{k});
    
    % Automatically find the Drive End time signal
    fn = fieldnames(S);
    DE_idx = contains(fn, '_DE_time');
    signal = S.(fn{DE_idx});
    
    % Time axis
    N = length(signal);
    t = (0:N-1)/fs;
    
    % Plot
    subplot(4,1,k)
    plot(t, signal)
    grid on
    xlabel('Time (s)')
    ylabel('Amplitude')
    title(['Drive End Signal - ', files{k}])
end

sgtitle('CWRU Drive End Vibration Signals')
