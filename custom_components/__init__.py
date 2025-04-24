from simpleeval import SimpleEval
if __name__ == "__main__":
    data = {
            "14603":14,
            "14604":23,
            "14602":0,
        }
    expression= "int(data['14603']/data['14604'])"
    s = SimpleEval(names={"data": data},functions={"round":round,"int":int})
    print(s.eval(expression))