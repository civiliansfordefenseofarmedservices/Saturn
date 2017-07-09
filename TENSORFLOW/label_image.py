import tensorflow as tf
import sys
from PIL import Image

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: {0} (image path)".format(sys.argv[0]))
        sys.exit(-1)

    #Path to where image we want to classify lives on disk
    image_path = "{0}".format(sys.argv[1])

    #Convert to parsed image
    image = Image.open(image_path)
    image_array = image.convert("RGB")

    #Load label file with no \r\n or \n at the end of each line.
    label_lines = [line.rstrip() for line in tf.gfile.GFile(
"tf_files/saturn_retrained_labels.txt")]

    #Unpersist graph from file.
    with tf.gfile.FastGFile("tf_files/saturn_retrained_graph.pb",
"rb") as graph_file:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(graph_file.read())
        _ = tf.import_graph_def(graph_def, name="")

    with tf.Session() as sess:
        #Feed the image_data as input to the graph and get first prediction
        softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

        predictions = sess.run(softmax_tensor, {'DecodeJpeg:0' : image_array})

        top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

        maxScore = 0
        label = "not suspect"

        for node_id in top_k:
            human_string = label_lines[node_id]
            score = predictions[0][node_id]
            if score > maxScore:
                maxScore = score
                label = "{0}".format(human_string)

    print("{0},{1},{2}".format(image_path, label, maxScore * 100.0))

    image.close()

if __name__ == "__main__":
    main()
