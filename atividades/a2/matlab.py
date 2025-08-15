% Lógica de controle do termostato no ThingSpeak
% 1. Configurações
readChannelID = 3035690;
writeChannelID = 3035690;
readAPIKey = '61PVPIZYS08IJUNC';
writeAPIKey = 'IN91SKW1JA4CZWQL';

tempLimite = 25; % Altere este valor para o limite de temperatura desejado
% 2. Ler a temperatura do canal
temp = thingSpeakRead(readChannelID, 'Field', 1, 'NumPoints', 1, 'ReadKey', readAPIKey);
% 3. Lógica de controle
if ~isempty(temp)
    if temp > tempLimite
        % Temperatura acima do limite, ligar o termostato
        status = 1; % Use 1 para 'on'
    else
        % Temperatura abaixo do limite, desligar o termostato
        status = 0; % Use 0 para 'off'
    end

    % 4. Escrever o novo status no campo 3 do canal
    thingSpeakWrite(writeChannelID, 'Field', 3, 'Value', status, 'WriteKey', writeAPIKey);

    disp(['Temperatura: ' num2str(temp) ' °C. Status do termostato: ' num2str(status)]);
else
    disp('Erro ao ler a temperatura do canal.');
end