import paddle
import paddlefsl.datasets as datasets
import paddlefsl.backbones as backbones
from paddlefsl.model_zoo import siamese


# Set computing device
paddle.set_device('gpu:1')


# """ ---------------------------------------------------------------------------------
# Config: Siamese, Few-Rel, Conv1D, 10 Ways, 1 Shot
max_len = 128
embedding_dim = 50
init_vector = backbones.GloVeRC(embedding_dim=embedding_dim)
TRAIN_DATASET = datasets.FewRel(mode='train', max_len=max_len, vector_initializer=init_vector)
VALID_DATASET = datasets.FewRel(mode='valid', max_len=max_len, vector_initializer=init_vector)
TEST_DATASET = datasets.FewRel(mode='valid', max_len=max_len, vector_initializer=init_vector)
WAYS = 10
SHOTS = 5
QUERY_NUM = 5
position_emb = backbones.RCPositionEmbedding(max_len=max_len, embedding_dim=embedding_dim)
conv1d = backbones.RCConv1D(max_len=max_len, embedding_size=position_emb.embedding_size, hidden_size=500)
norm = paddle.nn.Sequential(paddle.nn.LayerNorm(normalized_shape=conv1d.hidden_size), paddle.nn.Dropout(0.2))
MODEL = paddle.nn.Sequential(position_emb, conv1d, norm)
MODEL._full_name = 'glove50_cnn'
LR = 0.001
OPTIMIZER = paddle.optimizer.Adam(learning_rate=LR, parameters=MODEL.parameters())
EPOCHS = 50
TEST_EPOCHS = 10
EPISODES = 1000
REPORT_EPOCH = 1
LR_STEP_EPOCH = None
SAVE_MODEL_EPOCH = 10
SAVE_MODEL_ROOT = '~/trained_models'
TEST_PARAM_FILE = 'epoch50.params'
# ----------------------------------------------------------------------------------"""


def main():
    train_dir = siamese.meta_training(
        train_dataset=TRAIN_DATASET,
        valid_dataset=VALID_DATASET,
        model=MODEL,
        lr=LR,
        optimizer=OPTIMIZER,
        epochs=EPOCHS,
        episodes=EPISODES,
        ways=WAYS,
        shots=SHOTS,
        query_num=QUERY_NUM,
        report_epoch=REPORT_EPOCH,
        lr_step_epoch=LR_STEP_EPOCH,
        save_model_epoch=SAVE_MODEL_EPOCH,
        save_model_root=SAVE_MODEL_ROOT
    )
    print(train_dir)
    state_dict = paddle.load(train_dir + '/' + TEST_PARAM_FILE)
    MODEL.load_dict(state_dict)
    siamese.meta_testing(
        model=MODEL,
        test_dataset=TEST_DATASET,
        epochs=TEST_EPOCHS,
        episodes=EPISODES,
        ways=WAYS,
        shots=SHOTS,
        query_num=QUERY_NUM
    )


if __name__ == '__main__':
    main()
