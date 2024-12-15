# Consenso em sistemas síncronos

## Introdução
A solução serve para implementar e avaliar um <u>algoritmo de consenso distribuído</u> baseado em <u>inundação</u>. 

O primeiro código contém o algoritmo em si, que utiliza rodadas para transmitir mensagens entre os nós até que todos cheguem a um consenso. Já o segundo código cria um ambiente simulado usando o Mininet, no qual o algoritmo é executado de forma distribuída. </br>Ele também coleta métricas de desempenho, como o valor de consenso alcançado, o número de mensagens enviadas, recebidas e perdidas.

## Flooding (*flooding_consensus.py*)
### Inicialização
1. Cada nó (instância do script) possui um valor inicial que é derivado do último dígito de seu endereço IP <mark>(int(my_ip[-1]))</mark>. Isso corresponde à etapa de inicialização onde cada processo define seu valor inicial ($v_i$).
2. O conjunto <mark>known_values</mark> é iniciado com o valor do próprio nó, representando $Values^1_i$
3. O conjunto <mark>values_to_send</mark> contém os valores que serão enviados no início de cada rodada, equivalente ao envio de $Values^r_i - Values^{r-1}_i$
</br>
</br>
### Rodadas
O algoritmo avança em rodadas síncronas, com as seguintes etapas:

**a) Envio de mensagens**</br>
- Em cada rodada ($𝑟$):
    1. O nó seleciona os valores conhecidos no início da rodada (<mark>values_to_send</mark>) e os envia para seus pares usando **UDP**.
    2. Isso corresponde ao **B-multicast** no algoritmo teórico, onde cada nó envia valores ainda não conhecidos por outros processos.
    3. O envio é feito dentro de um intervalo de tempo definido por <mark>ROUND_DURATION</mark>, garantindo a sincronização.

**b) Recepção de mensagens**</br>
- O nó escuta continuamente na porta UDP por mensagens recebidas de outros nós.
- Quando recebe uma mensagem, adiciona os valores na mensagem ao conjunto <mark>known_values</mark>, que representa $Values^{r+1}_i$ sendo atualizado ao longo da rodada.
- Essa etapa implementa a parte onde o nó processa as mensagens recebidas $(B-deliver)$

**c) Sincronização**</br>
As rodadas são sincronizadas por meio do intervalo de tempo definido em <mark>ROUND_DURATION</mark>, garantindo que todos os nós avancem juntos para a próxima rodada, como esperado em sistemas síncronos.
</br>
</br>
### Finalização
Após todas as rodadas $(f+1)$, o nó determina o **valor de consenso** como o menor valor no conjunto <mark>known_values</mark>, em conformidade com a especificação do algoritmo teórico:</br>
$d_i = minimum(Values^{f+1}_i)$
</br>
</br>
### Paralelos com algoritmo
| Algoritmo Teórico | Implementação no Código |
| --- | --- |
| Inicialização $(Values^1_i)$ | <mark>known_values</mark> inicializado com o valor derivado do IP. |
| Envio de novos valores $(B-multicast)$ | <mark>values_to_send</mark> e envio UDP para os pares |
| Recepção e união de valores $(B-deliver)$ | Recebimento UDP e adição ao conjunto <mark>known_values</mark> |
| Rodadas síncronas $(1<= r <= f+1)$ | Controle pelo intervalo <mark>ROUND_DURATION</mark>. |
| Escolha do consenso $(d_i=min)$ | Determinação do menor valor em <mark>known_values</mark>.|

## Mininet (*topology.py*)
O segundo código complementa o primeiro ao fornecer um ambiente controlado e automatizado para testar e avaliar o algoritmo de consenso baseado em inundação. Ele utiliza o <mark>Mininet</mark>, um simulador de redes, para criar uma topologia de rede simples com hosts e links configuráveis.

### Execução do Algoritmo de Consenso
O script utiliza o Mininet para instanciar os hosts e, em seguida:
- Obtém os endereços IP de todos os nós.
- Gera um comando para executar o script <mark>flooding_consensus.py</mark> em cada host. O comando inclui:
    - O IP do host como argumento principal.
    - Os IPs dos outros nós como peers para o algoritmo de consenso.
- Inicia o script em cada host usando o método host.cmd, direcionando a saída para arquivos de log individuais na pasta log.

Após executar o algoritmo por um período definido (7 segundos no código), o script:
- Lê os arquivos de log gerados por cada host.
- Extrai a última linha dos arquivos, que contém as métricas em formato JSON geradas pelo primeiro script.
- Coleta informações como:
    - O valor de consenso alcançado por cada nó.
    - O número de mensagens enviadas, recebidas e perdidas.

## Resumo
- **O primeiro código (algoritmo de consenso)** é a implementação do protocolo de consenso distribuído.
- **O segundo código (simulação com Mininet)** cria o ambiente necessário para testar e avaliar o algoritmo em um cenário próximo ao real, com vários nós distribuídos em uma rede.
</br>
</br>

## Exemplo de execução
Este exemplo (arquivo <mark>h5_output.log</mark> na pasta de log's) descreve a execução do algoritmo, no qual o nó <marK>10.0.0.5</mark> participa da comunicação para alcançar um valor de consenso entre os outros nós da rede.

#### Início:
- O nó inicia a execução conhecendo apenas o valor 5.
- Em cada rodada, o nó envia os valores que conhece para os demais nós da rede (endereços: <mark>10.0.0.1</mark> até <mark>10.0.0.6</mark>).

#### Progressão das Rodadas:

- O algoritmo realiza <mark>5 rodadas</mark> de comunicação.
- Em cada rodada, o nó compartilha os valores conhecidos e recebe novos valores de outros nós. O conjunto de <mark>known_values</mark> é atualizado conforme as mensagens recebidas.

### Finalização:

- Ao final das rodadas, o algoritmo conclui o valor de consenso como 1.
- São registrados os métricas finais:
    - **Mensagens enviadas**: 25.
    - **Mensagens recebidas**: 25.
    - **Mensagens perdidas**: 0.
    - **Duração total**: 5.0107 segundos.
    - **Valores conhecidos**: <mark>[1, 2, 3, 4, 5, 6]</mark>.

O algoritmo termina com sucesso, garantindo que o consenso foi atingido de forma determinística.