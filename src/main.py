import argparse
from LOGALLM.LOGA_pipeline import LOGA_pipeline



if __name__ == "__main__":
    print("<--------------- LoGicArgLLM --------------->")

    parser = argparse.ArgumentParser(description="LOGALLM")
    parser.add_argument(
        "-m", "--mode", type=str, default="ui", help="ui-WebPageUI, nd-NewDataset"
    ) # 模式 

    parser.add_argument(
        "-dp", "--dataset", type=str, help="Dataset Path"
    )

    parser.add_argument(
        "-llm", "--model", type=str, default="deepseek"
    )


    args = parser.parse_args()
    the_mode = args.mode
    the_data = args.dataset
    the_llm = args.model
    print(the_data, the_mode)
    pipeline = LOGA_pipeline(the_mode, the_data, the_llm)









    



